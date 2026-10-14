"""
MetricMind AI Agent Package
Defines the metrics catalogue, semantic query contract, Cube client, and AI agent.
"""
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

__all__ = [
    "APPROVED_MEASURES",
    "APPROVED_DIMENSIONS",
    "APPROVED_MEMBERS",
    "APPROVED_OPERATORS",
    "METRICS_CATALOG",
    "get_catalog_prompt_context",
    "CubeQuery",
    "CubeFilter",
    "CubeTimeDimension",
    "CubeClient",
    "CubeClientError",
    "CubeConnectionError",
    "CubeQueryError",
    "MetricMindAgent",
    "AgentError",
    "MissingApiKeyError",
    "QueryGenerationError",
]
