"""
Tests for MetricMind AI Query Contract and Metrics Catalogue
Verifies strict validation rules, member allowlists, SQL-injection prevention,
and optional live semantic execution against Cube.
"""

import pytest
import requests
from pydantic import ValidationError

from backend.ai_agent.metrics_catalog import (
    APPROVED_MEASURES,
    APPROVED_DIMENSIONS,
    APPROVED_MEMBERS,
    APPROVED_OPERATORS,
    METRICS_CATALOG,
    get_catalog_prompt_context,
)
from backend.ai_agent.query_contract import (
    CubeQuery,
    CubeFilter,
    CubeTimeDimension,
)


# ============================================================
# 1. METRICS CATALOGUE TESTS
# ============================================================

def test_metrics_catalog_integrity():
    """Verify all approved measures and dimensions are present and correctly typed."""
    assert len(APPROVED_MEASURES) == 7
    expected_measures = {
        "Sales.totalRevenue",
        "Sales.totalCost",
        "Sales.totalMargin",
        "Sales.totalOrders",
        "Sales.totalQuantity",
        "Sales.averageOrderValue",
        "Sales.marginRate",
    }
    assert set(APPROVED_MEASURES.keys()) == expected_measures

    assert len(APPROVED_DIMENSIONS) == 8
    expected_dimensions = {
        "Sales.orderId",
        "Sales.orderDate",
        "Sales.quarter",
        "Sales.region",
        "Sales.country",
        "Sales.productName",
        "Sales.category",
        "Sales.customerId",
    }
    assert set(APPROVED_DIMENSIONS.keys()) == expected_dimensions

    # Combined members set
    assert len(APPROVED_MEMBERS) == 15
    assert set(APPROVED_MEMBERS) == expected_measures | expected_dimensions


def test_metrics_catalog_metadata():
    """Verify metadata descriptions and properties exist for each measure."""
    for measure, meta in APPROVED_MEASURES.items():
        assert "description" in meta and len(meta["description"]) > 5
        assert "title" in meta
        assert "type" in meta

    for dim, meta in APPROVED_DIMENSIONS.items():
        assert "description" in meta and len(meta["description"]) > 5
        assert "title" in meta
        assert "type" in meta


def test_catalog_prompt_context():
    """Verify prompt context string includes rules and member names for LLM."""
    context = get_catalog_prompt_context()
    assert "Sales.totalRevenue" in context
    assert "Sales.quarter" in context
    assert "Sales.country" in context
    assert "APPROVED FILTER OPERATORS" in context
    assert "CRITICAL RULE" in context


# ============================================================
# 2. QUERY CONTRACT - VALID QUERIES
# ============================================================

def test_valid_cube_query_contract():
    """Verify valid Cube query parses correctly and serializes to Cube payload."""
    query = CubeQuery(
        measures=["Sales.totalRevenue", "Sales.totalOrders"],
        dimensions=["Sales.quarter"],
        filters=[
            CubeFilter(
                member="Sales.region",
                operator="equals",
                values=["Europe"],
            )
        ],
        order={"Sales.totalRevenue": "desc"},
        limit=5,
    )

    assert query.measures == ["Sales.totalRevenue", "Sales.totalOrders"]
    assert query.dimensions == ["Sales.quarter"]
    assert len(query.filters) == 1
    assert query.filters[0].member == "Sales.region"
    assert query.order == {"Sales.totalRevenue": "desc"}
    assert query.limit == 5

    payload = query.to_cube_payload()
    assert "query" in payload
    q = payload["query"]
    assert q["measures"] == ["Sales.totalRevenue", "Sales.totalOrders"]
    assert q["dimensions"] == ["Sales.quarter"]
    assert q["filters"] == [
        {"member": "Sales.region", "operator": "equals", "values": ["Europe"]}
    ]
    assert q["order"] == {"Sales.totalRevenue": "desc"}
    assert q["limit"] == 5


def test_valid_time_dimension():
    """Verify time dimension contract behaves correctly."""
    query = CubeQuery(
        measures=["Sales.totalRevenue"],
        timeDimensions=[
            CubeTimeDimension(
                dimension="Sales.orderDate",
                dateRange=["2025-01-01", "2025-06-30"],
                granularity="month",
            )
        ],
    )
    payload = query.to_cube_payload()
    assert len(payload["query"]["timeDimensions"]) == 1
    td = payload["query"]["timeDimensions"][0]
    assert td["dimension"] == "Sales.orderDate"
    assert td["granularity"] == "month"


# ============================================================
# 3. QUERY CONTRACT - REJECTION TESTS (SAFETY & VALIDATION)
# ============================================================

def test_reject_unknown_measure():
    """Verify unapproved measure name is rejected with ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        CubeQuery(measures=["Sales.profitMarginPercentage"])
    assert "Unknown measure 'Sales.profitMarginPercentage'" in str(exc_info.value)


def test_reject_unknown_dimension():
    """Verify unapproved dimension name is rejected with ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        CubeQuery(
            measures=["Sales.totalRevenue"],
            dimensions=["Sales.city"],
        )
    assert "Unknown dimension 'Sales.city'" in str(exc_info.value)


def test_reject_unknown_filter_member():
    """Verify filter on unknown member is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CubeFilter(
            member="Sales.nonExistentColumn",
            operator="equals",
            values=["Test"],
        )
    assert "Unknown filter member" in str(exc_info.value)


def test_reject_invalid_filter_operator():
    """Verify unsupported filter operator is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CubeFilter(
            member="Sales.region",
            operator="like",
            values=["%Europe%"],
        )
    assert "Unsupported filter operator 'like'" in str(exc_info.value)


def test_reject_invalid_order_direction():
    """Verify invalid order direction is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CubeQuery(
            measures=["Sales.totalRevenue"],
            order={"Sales.totalRevenue": "ascending"},
        )
    assert "Order direction 'ascending' must be 'asc' or 'desc'" in str(exc_info.value)


def test_reject_invalid_order_member():
    """Verify ordering by an unknown member is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CubeQuery(
            measures=["Sales.totalRevenue"],
            order={"Sales.fakeColumn": "desc"},
        )
    assert "Order member 'Sales.fakeColumn' is not an approved Cube measure or dimension" in str(exc_info.value)


def test_reject_empty_query():
    """Verify query with no measures and no dimensions is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CubeQuery(limit=10)
    assert "A Cube query must include at least one measure or dimension" in str(exc_info.value)


def test_reject_invalid_limit():
    """Verify limit < 1 or limit > 1000 is rejected."""
    with pytest.raises(ValidationError):
        CubeQuery(measures=["Sales.totalRevenue"], limit=0)

    with pytest.raises(ValidationError):
        CubeQuery(measures=["Sales.totalRevenue"], limit=5000)


def test_reject_sql_injection_in_filter():
    """Verify raw SQL injection patterns in filter values are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CubeFilter(
            member="Sales.region",
            operator="equals",
            values=["Europe'; DROP TABLE fct_sales; --"],
        )
    assert "Potentially unsafe raw SQL detected" in str(exc_info.value)


def test_reject_sql_injection_in_measure():
    """Verify raw SQL keywords in measure strings are rejected."""
    with pytest.raises(ValidationError):
        CubeQuery(measures=["SELECT * FROM fct_sales"])


def test_extra_fields_forbidden():
    """Verify extra/unknown fields on query contract are rejected."""
    with pytest.raises(ValidationError):
        CubeQuery(
            measures=["Sales.totalRevenue"],
            extraRawSql="SELECT 1",
        )


# ============================================================
# 4. LIVE CUBE EXECUTION WITH CONTRACT
# ============================================================

def test_live_cube_query_with_contract():
    """
    Executes a verified query contract against the live Cube Docker instance (port 4000).
    Verifies that the generated contract payload succeeds with 200 OK and returns data.
    """
    contract = CubeQuery(
        measures=["Sales.totalRevenue", "Sales.totalOrders"],
        dimensions=["Sales.quarter"],
        filters=[
            CubeFilter(
                member="Sales.region",
                operator="equals",
                values=["Europe"],
            )
        ],
        order={"Sales.totalRevenue": "desc"},
        limit=4,
    )

    cube_payload = contract.to_cube_payload()

    try:
        response = requests.post(
            "http://localhost:4000/cubejs-api/v1/load",
            json=cube_payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        pytest.skip("Cube server on port 4000 is not reachable (skipping live integration test)")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0

    first_row = data["data"][0]
    assert "Sales.quarter" in first_row
    assert "Sales.totalRevenue" in first_row
    assert "Sales.totalOrders" in first_row


# ============================================================
# 5. CUBE API CLIENT TESTS
# ============================================================

from unittest.mock import MagicMock
from backend.cube_client import (
    CubeClient,
    CubeClientError,
    CubeConnectionError,
    CubeQueryError,
)
from backend.ai_agent.agent import (
    MetricMindAgent,
    AgentError,
    MissingApiKeyError,
    QueryGenerationError,
)


def test_cube_client_invalid_argument():
    """Verify passing non-CubeQuery raises ValueError."""
    client = CubeClient()
    with pytest.raises(ValueError):
        client.execute_query({"not": "a CubeQuery"})


def test_cube_client_live_execution():
    """Verify CubeClient connects and queries live Cube instance."""
    client = CubeClient()
    query = CubeQuery(
        measures=["Sales.totalRevenue", "Sales.totalOrders"],
        limit=1,
    )
    try:
        rows = client.execute_query(query)
    except CubeConnectionError:
        pytest.skip("Cube server on port 4000 is not reachable")

    assert isinstance(rows, list)
    assert len(rows) == 1
    assert "Sales.totalRevenue" in rows[0]
    assert "Sales.totalOrders" in rows[0]


def test_cube_client_health_check():
    """Verify health_check against live Cube or mocked endpoint."""
    client = CubeClient()
    # Live or graceful fallback
    is_healthy = client.health_check()
    assert isinstance(is_healthy, bool)


def test_cube_client_mock_connection_error():
    """Verify connection errors raise CubeConnectionError with safe message."""
    mock_session = MagicMock()
    mock_session.post.side_effect = requests.exceptions.ConnectionError("Connection refused")
    client = CubeClient(session=mock_session)

    query = CubeQuery(measures=["Sales.totalRevenue"])
    with pytest.raises(CubeConnectionError) as exc_info:
        client.execute_query(query)
    assert "Unable to connect to Cube semantic layer" in str(exc_info.value)


def test_cube_client_mock_timeout():
    """Verify timeout raises CubeConnectionError."""
    mock_session = MagicMock()
    mock_session.post.side_effect = requests.exceptions.Timeout("Request timed out")
    client = CubeClient(session=mock_session, timeout=2.0)

    query = CubeQuery(measures=["Sales.totalRevenue"])
    with pytest.raises(CubeConnectionError) as exc_info:
        client.execute_query(query)
    assert "timed out after 2.0s" in str(exc_info.value)


def test_cube_client_mock_http_error():
    """Verify Cube HTTP errors raise CubeQueryError without exposing secrets."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Invalid dimension in Cube model"}
    mock_session.post.return_value = mock_response

    client = CubeClient(session=mock_session)
    query = CubeQuery(measures=["Sales.totalRevenue"])

    with pytest.raises(CubeQueryError) as exc_info:
        client.execute_query(query)
    assert "Cube error: Invalid dimension in Cube model" in str(exc_info.value)


def test_cube_client_mock_invalid_json():
    """Verify non-JSON response raises CubeQueryError."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("No JSON")
    mock_session.post.return_value = mock_response

    client = CubeClient(session=mock_session)
    query = CubeQuery(measures=["Sales.totalRevenue"])

    with pytest.raises(CubeQueryError) as exc_info:
        client.execute_query(query)
    assert "Cube response was not valid JSON" in str(exc_info.value)


# ============================================================
# 6. METRICMIND AI AGENT TESTS
# ============================================================

def test_agent_missing_api_key():
    """Verify agent raises MissingApiKeyError when no key is provided and real LLM is called."""
    agent = MetricMindAgent(api_key="", llm_caller=None)
    with pytest.raises(MissingApiKeyError):
        agent._call_gemini_rest("test prompt")


def test_agent_empty_question():
    """Verify empty question raises QueryGenerationError."""
    agent = MetricMindAgent(llm_caller=lambda p, j: "{}")
    with pytest.raises(QueryGenerationError):
        agent.generate_cube_query("")


def test_agent_valid_query_generation():
    """Verify agent maps question to validated CubeQuery using mocked LLM output."""
    mock_llm_json = """
    {
        "measures": ["Sales.totalRevenue"],
        "dimensions": ["Sales.quarter"],
        "filters": [
            {
                "member": "Sales.region",
                "operator": "equals",
                "values": ["Europe"]
            }
        ],
        "order": {
            "Sales.totalRevenue": "desc"
        },
        "limit": 1
    }
    """
    agent = MetricMindAgent(llm_caller=lambda p, j: mock_llm_json)
    query = agent.generate_cube_query("Which quarter had the highest revenue in Europe?")

    assert isinstance(query, CubeQuery)
    assert query.measures == ["Sales.totalRevenue"]
    assert query.dimensions == ["Sales.quarter"]
    assert len(query.filters) == 1
    assert query.filters[0].member == "Sales.region"
    assert query.filters[0].values == ["Europe"]
    assert query.order == {"Sales.totalRevenue": "desc"}
    assert query.limit == 1


def test_agent_markdown_fence_json_handling():
    """Verify agent strips markdown code fences from LLM responses."""
    fenced_output = """```json
    {
        "measures": ["Sales.totalOrders"],
        "dimensions": ["Sales.country"]
    }
    ```"""
    agent = MetricMindAgent(llm_caller=lambda p, j: fenced_output)
    query = agent.generate_cube_query("How many orders per country?")

    assert query.measures == ["Sales.totalOrders"]
    assert query.dimensions == ["Sales.country"]


def test_agent_reject_unknown_member_from_llm():
    """Verify agent rejects LLM hallucinations with unapproved members."""
    hallucinated_output = """
    {
        "measures": ["Sales.inventedProfitMetric"],
        "dimensions": ["Sales.quarter"]
    }
    """
    mock_cube = MagicMock()
    agent = MetricMindAgent(llm_caller=lambda p, j: hallucinated_output, cube_client=mock_cube)

    with pytest.raises(QueryGenerationError) as exc_info:
        agent.generate_cube_query("What is the invented profit metric?")

    assert "Unknown measure 'Sales.inventedProfitMetric'" in str(exc_info.value)
    # Ensure invalid query never reached Cube
    mock_cube.execute_query.assert_not_called()


def test_agent_reject_sql_injection_from_llm():
    """Verify agent rejects raw SQL in filter values from malicious/compromised LLM output."""
    injection_output = """
    {
        "measures": ["Sales.totalRevenue"],
        "filters": [
            {
                "member": "Sales.country",
                "operator": "equals",
                "values": ["Germany'; DROP TABLE fct_sales; --"]
            }
        ]
    }
    """
    mock_cube = MagicMock()
    agent = MetricMindAgent(llm_caller=lambda p, j: injection_output, cube_client=mock_cube)

    with pytest.raises(QueryGenerationError) as exc_info:
        agent.generate_cube_query("Show me Germany")

    assert "Potentially unsafe raw SQL detected" in str(exc_info.value)
    mock_cube.execute_query.assert_not_called()


def test_agent_reject_malformed_json_from_llm():
    """Verify non-JSON response from LLM raises QueryGenerationError."""
    agent = MetricMindAgent(llm_caller=lambda p, j: "I am unable to answer this question.")
    with pytest.raises(QueryGenerationError) as exc_info:
        agent.generate_cube_query("Some question")
    assert "LLM did not return valid JSON" in str(exc_info.value)


def test_agent_synthesize_answer_deterministic_single_measure():
    """Verify single-measure queries format deterministically."""
    agent = MetricMindAgent(llm_caller=lambda p, j: "")
    query = CubeQuery(measures=["Sales.totalRevenue"])
    data = [{"Sales.totalRevenue": "5720530.61"}]

    answer = agent.synthesize_answer("What is the total revenue?", query, data)
    assert "$5,720,530.61" in answer
    assert "total revenue" in answer.lower()


def test_agent_synthesize_answer_empty_data():
    """Verify empty data returns graceful message."""
    agent = MetricMindAgent(llm_caller=lambda p, j: "")
    query = CubeQuery(measures=["Sales.totalRevenue"])
    answer = agent.synthesize_answer("Question with no data", query, [])
    assert "No sales data is available" in answer


def test_agent_full_answer_pipeline_mocked():
    """Verify end-to-end agent pipeline with mocked LLM and Cube client."""
    mock_query_json = """
    {
        "measures": ["Sales.totalRevenue"],
        "dimensions": ["Sales.quarter"],
        "order": {"Sales.totalRevenue": "desc"},
        "limit": 1
    }
    """
    mock_cube_data = [{"Sales.quarter": "Q2", "Sales.totalRevenue": "1484038.25"}]
    mock_synthesis_text = "Q2 had the highest revenue with $1,484,038.25."

    def mock_llm(prompt, is_json):
        if is_json:
            return mock_query_json
        return mock_synthesis_text

    mock_client = MagicMock()
    mock_client.execute_query.return_value = mock_cube_data

    agent = MetricMindAgent(llm_caller=mock_llm, cube_client=mock_client)
    result = agent.answer_question("Which quarter had the highest revenue?")

    assert result["question"] == "Which quarter had the highest revenue?"
    assert result["answer"] == mock_synthesis_text
    assert result["data"] == mock_cube_data
    assert result["query"]["measures"] == ["Sales.totalRevenue"]
    assert result["query"]["dimensions"] == ["Sales.quarter"]
    mock_client.execute_query.assert_called_once()


# ============================================================
# 7. FASTAPI /questions/answer INTEGRATION TESTS
# ============================================================

from fastapi.testclient import TestClient
from backend.main import app

api_client = TestClient(app)


def test_api_cube_health_endpoint():
    """Verify GET /cube-health returns status and connection state."""
    response = api_client.get("/cube-health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cube_connected" in data
    assert isinstance(data["cube_connected"], bool)


def test_api_answer_question_with_injected_ai_agent():
    """Verify /questions/answer uses AI Agent pipeline when agent is available."""
    mock_agent = MagicMock()
    mock_agent.answer_question.return_value = {
        "question": "Which product generated the most revenue?",
        "answer": "Analytics Suite generated the highest revenue with $1,234,567.89.",
        "query": {
            "measures": ["Sales.totalRevenue"],
            "dimensions": ["Sales.productName"],
            "order": {"Sales.totalRevenue": "desc"},
            "limit": 1,
        },
        "data": [{"Sales.productName": "Analytics Suite", "Sales.totalRevenue": "1234567.89"}],
    }

    # Inject mock agent into app state
    app.state.ai_agent = mock_agent
    try:
        response = api_client.post(
            "/questions/answer",
            json={"question": "Which product generated the most revenue?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "Which product generated the most revenue?"
        assert "Analytics Suite" in data["answer"]
        assert data["source"] == "ai_agent"
        assert data["query"]["measures"] == ["Sales.totalRevenue"]
        mock_agent.answer_question.assert_called_once_with("Which product generated the most revenue?")
    finally:
        app.state.ai_agent = None


def test_api_answer_question_ai_failure_graceful_fallback():
    """Verify /questions/answer gracefully falls back to deterministic answer if AI Agent fails."""
    mock_failing_agent = MagicMock()
    mock_failing_agent.answer_question.side_effect = RuntimeError("Simulated Gemini quota exceeded")

    app.state.ai_agent = mock_failing_agent
    try:
        response = api_client.post(
            "/questions/answer",
            json={"question": "Which quarter had the highest revenue?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "Which quarter had the highest revenue?"
        # Fallback answered successfully
        assert "Q2" in data["answer"]
        assert "highest revenue" in data["answer"].lower()
        assert data["source"] == "deterministic_fallback"
    finally:
        app.state.ai_agent = None


def test_api_answer_question_deterministic_fallback_when_unconfigured(monkeypatch):
    """Verify /questions/answer operates in deterministic fallback mode when AI is unconfigured."""
    app.state.ai_agent = None
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = api_client.post(
        "/questions/answer",
        json={"question": "What is the total revenue?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the total revenue?"
    assert "$5,720,530.61" in data["answer"]
    assert data["source"] == "deterministic_fallback"


def test_agent_gemini_503_error_handling():
    """Verify agent properly raises AgentError when Gemini returns HTTP 503 high demand."""
    from unittest.mock import patch, Mock
    agent = MetricMindAgent(api_key="test-key", llm_caller=None)
    mock_resp = Mock()
    mock_resp.status_code = 503
    mock_resp.text = "Service Unavailable: The model is overloaded."
    mock_resp.json.return_value = {"error": {"message": "The model is overloaded. Please try again later."}}

    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(AgentError) as exc_info:
            agent._call_gemini_rest("test prompt")
        assert "HTTP 503" in str(exc_info.value)
        assert "The model is overloaded" in str(exc_info.value)


def test_api_answer_question_gemini_503_graceful_fallback():
    """Verify /questions/answer gracefully falls back to deterministic answer when Gemini returns HTTP 503."""
    mock_agent = MagicMock()
    mock_agent.answer_question.side_effect = AgentError(
        "Gemini API returned HTTP 503: The model is overloaded. Please try again later."
    )

    app.state.ai_agent = mock_agent
    try:
        response = api_client.post(
            "/questions/answer",
            json={"question": "Which country generated the most revenue?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "Which country generated the most revenue?"
        assert "Spain" in data["answer"]
        assert data["source"] == "deterministic_fallback"
        assert data["query"] is None
    finally:
        app.state.ai_agent = None

