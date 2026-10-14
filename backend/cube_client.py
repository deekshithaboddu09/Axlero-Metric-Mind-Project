"""
MetricMind Cube API Client
Executes validated Cube semantic queries via Cube REST API (/cubejs-api/v1/load).
Does not construct or execute raw SQL.
Handles connection errors, timeouts, and Cube error responses safely.
"""

import os
import requests
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from backend.ai_agent.query_contract import CubeQuery

load_dotenv()

DEFAULT_CUBE_URL = "http://localhost:4000/cubejs-api/v1/load"
DEFAULT_TIMEOUT = 15.0


class CubeClientError(Exception):
    """Base exception for Cube client operations."""
    pass


class CubeConnectionError(CubeClientError):
    """Raised when Cube service is unreachable or connection times out."""
    pass


class CubeQueryError(CubeClientError):
    """Raised when Cube responds with a query error (e.g. 400 or JSON error)."""
    pass


class CubeClient:
    """
    HTTP client for querying Cube's REST API.
    """
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = (
            base_url
            or os.getenv("CUBE_API_URL")
            or DEFAULT_CUBE_URL
        )
        self.timeout = timeout
        self.session = session or requests.Session()

    def execute_query(self, query: CubeQuery) -> List[Dict[str, Any]]:
        """
        Executes a validated CubeQuery against Cube's REST API.
        Returns the data rows list (e.g. [{"Sales.quarter": "Q2", "Sales.totalRevenue": "1484038.25"}]).
        """
        if not isinstance(query, CubeQuery):
            raise ValueError("Query must be an instance of CubeQuery.")

        payload = query.to_cube_payload()
        return self.execute_payload(payload)

    def execute_payload(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Sends raw Cube query payload (e.g. {"query": {...}}) to the Cube REST endpoint.
        """
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as exc:
            raise CubeConnectionError(
                f"Cube query timed out after {self.timeout}s."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise CubeConnectionError(
                "Unable to connect to Cube semantic layer. Ensure the Cube service is running."
            ) from exc
        except Exception as exc:
            raise CubeConnectionError(
                f"Unexpected connection error querying Cube: {exc}"
            ) from exc

        if response.status_code != 200:
            error_msg = f"Cube returned HTTP {response.status_code}"
            try:
                err_data = response.json()
                if "error" in err_data:
                    error_msg = f"Cube error: {err_data['error']}"
                elif "message" in err_data:
                    error_msg = f"Cube error: {err_data['message']}"
            except Exception:
                pass
            raise CubeQueryError(error_msg)

        try:
            data = response.json()
        except Exception as exc:
            raise CubeQueryError("Cube response was not valid JSON.") from exc

        if not isinstance(data, dict):
            raise CubeQueryError("Unexpected response format from Cube.")

        if "error" in data:
            raise CubeQueryError(f"Cube error: {data['error']}")

        rows = data.get("data", [])
        if not isinstance(rows, list):
            raise CubeQueryError("Cube response 'data' field is not a list.")

        return rows

    def health_check(self) -> bool:
        """
        Verifies whether Cube server is reachable and responsive.
        """
        try:
            meta_url = self.base_url.replace("/load", "/meta")
            res = self.session.get(meta_url, timeout=3.0)
            return res.status_code == 200
        except Exception:
            return False
