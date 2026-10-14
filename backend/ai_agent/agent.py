"""
MetricMind AI Agent
Translates natural-language business questions into validated Cube semantic queries,
executes them via CubeClient, and synthesizes data into concise executive answers.
Uses Google Gemini with strict structured output. Never accepts or generates raw SQL.
"""

import json
import os
import re
from typing import Any, Callable, Dict, List, Optional
from dotenv import load_dotenv

from backend.ai_agent.metrics_catalog import get_catalog_prompt_context
from backend.ai_agent.query_contract import CubeQuery
from backend.cube_client import CubeClient, CubeClientError

load_dotenv()


class AgentError(Exception):
    """Base exception for AI Agent errors."""
    pass


class MissingApiKeyError(AgentError):
    """Raised when the required LLM API key is not configured."""
    pass


class QueryGenerationError(AgentError):
    """Raised when the LLM produces invalid, unparseable, or unapproved query contracts."""
    pass


class MetricMindAgent:
    """
    AI Agent that connects natural language questions to the Cube Semantic Layer.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        cube_client: Optional[CubeClient] = None,
        llm_caller: Optional[Callable[[str, bool], str]] = None,
    ):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.cube_client = cube_client or CubeClient()
        # llm_caller can be injected for testing or mocking:
        # callable signature: (prompt: str, json_mode: bool) -> response_text
        self.llm_caller = llm_caller or self._call_gemini_rest

    def _call_gemini_rest(self, prompt: str, json_mode: bool = False) -> str:
        """
        Calls Google Gemini REST API v1beta generateContent endpoint.
        """
        if not self.api_key:
            raise MissingApiKeyError(
                "GEMINI_API_KEY environment variable is not configured."
            )

        import requests

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        generation_config: Dict[str, Any] = {"temperature": 0.0}
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": generation_config,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=20.0,
            )
        except requests.exceptions.RequestException as exc:
            raise AgentError(f"Gemini API request failed: {exc}") from exc

        if response.status_code == 429:
            raise AgentError(
                "Gemini API quota exceeded or rate limited. Please try again later."
            )
        if response.status_code != 200:
            error_detail = response.text[:200]
            try:
                err_json = response.json()
                if "error" in err_json:
                    error_detail = err_json["error"].get("message", error_detail)
            except Exception:
                pass
            raise AgentError(f"Gemini API returned HTTP {response.status_code}: {error_detail}")

        try:
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise AgentError("Gemini returned empty response candidates.")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise AgentError("Gemini candidate contains no content parts.")
            return parts[0].get("text", "").strip()
        except Exception as exc:
            raise AgentError(f"Failed to parse Gemini response: {exc}") from exc

    def generate_cube_query(self, question: str) -> CubeQuery:
        """
        Translates a natural language question into a validated CubeQuery contract.
        Rejects invalid or unapproved members before execution.
        """
        if not question or not question.strip():
            raise QueryGenerationError("Question cannot be empty.")

        catalog_context = get_catalog_prompt_context()

        prompt = f"""{catalog_context}

### TASK:
Translate the following user question into a strict JSON Cube query object matching the schema below.

JSON Schema:
{{
  "measures": ["<Approved Measure Name>"],
  "dimensions": ["<Approved Dimension Name>"],
  "filters": [
    {{
      "member": "<Approved Member Name>",
      "operator": "equals" | "notEquals" | "contains" | "notContains" | "gt" | "gte" | "lt" | "lte" | "set" | "notSet",
      "values": ["<value>"]
    }}
  ],
  "order": {{
    "<Approved Measure or Dimension>": "asc" | "desc"
  }},
  "limit": <integer 1 to 1000>
}}

### CRITICAL RULES:
1. ONLY return the JSON object. Do not include markdown code fences or explanations.
2. NEVER generate raw SQL.
3. Every measure must start with "Sales.".
4. Every dimension must start with "Sales.".
5. If the user asks for highest/maximum/top, order by the measure desc with limit 1.
6. If the user asks for lowest/minimum/least, order by the measure asc with limit 1.

User Question: "{question.strip()}"
"""

        raw_json = self.llm_caller(prompt, True)

        # Clean possible markdown fences if returned
        cleaned_json = raw_json.strip()
        if cleaned_json.startswith("```"):
            cleaned_json = re.sub(r"^```(?:json)?\s*", "", cleaned_json)
            cleaned_json = re.sub(r"\s*```$", "", cleaned_json)

        try:
            parsed_dict = json.loads(cleaned_json)
        except json.JSONDecodeError as exc:
            raise QueryGenerationError(
                f"LLM did not return valid JSON: {cleaned_json[:150]}"
            ) from exc

        # Strict validation with Pydantic CubeQuery
        try:
            validated_query = CubeQuery(**parsed_dict)
        except Exception as exc:
            raise QueryGenerationError(
                f"Generated query violates Cube query contract: {exc}"
            ) from exc

        return validated_query

    def synthesize_answer(
        self,
        question: str,
        query: CubeQuery,
        data: List[Dict[str, Any]],
    ) -> str:
        """
        Generates a concise, business-focused answer based ONLY on the returned Cube data.
        """
        if not data:
            return "No sales data is available matching the requested criteria."

        # Deterministic formatting for single-row aggregations
        if len(data) == 1:
            row = data[0]
            if len(query.measures) == 1 and not query.dimensions:
                m = query.measures[0]
                val = row.get(m, 0)
                try:
                    num_val = float(val)
                    label = m.replace("Sales.", "")
                    # Convert camelCase to title
                    label_title = re.sub(r"([A-Z])", r" \1", label).strip().lower()
                    if "revenue" in m.lower() or "cost" in m.lower() or "margin" in m.lower():
                        return f"The {label_title} is ${num_val:,.2f}."
                    elif "orders" in m.lower() or "quantity" in m.lower():
                        return f"The total {label_title} is {int(num_val):,}."
                except (ValueError, TypeError):
                    pass

        # Call synthesis prompt with data context
        prompt = f"""You are a professional business intelligence assistant for MetricMind.
A user asked: "{question}"

The semantic layer (Cube) returned the following aggregated data records:
{json.dumps(data, indent=2)}

Task: Provide a concise, professional 1-2 sentence answer to the user's question citing the numbers accurately.
Do not speculate or cite numbers that are not in the data above.
"""
        try:
            return self.llm_caller(prompt, False)
        except Exception:
            # Safe fallback summary formatting if LLM synthesis fails
            summary_parts = []
            for k, v in data[0].items():
                label = k.replace("Sales.", "")
                summary_parts.append(f"{label}: {v}")
            return f"Query result: {', '.join(summary_parts)}."

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Full pipeline:
        1. Natural language question -> CubeQuery (validated)
        2. CubeQuery -> CubeClient -> PostgreSQL -> Data rows
        3. Data rows -> Executive synthesized answer
        Returns dict with question, answer, query metadata, and data.
        """
        validated_query = self.generate_cube_query(question)
        data = self.cube_client.execute_query(validated_query)
        answer = self.synthesize_answer(question, validated_query, data)

        return {
            "question": question,
            "answer": answer,
            "query": validated_query.model_dump(exclude_none=True),
            "data": data,
        }
