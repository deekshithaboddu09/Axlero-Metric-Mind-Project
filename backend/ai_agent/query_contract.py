"""
MetricMind AI Query Contract
Defines strict Pydantic models for semantic Cube queries.
Validates all members, dimensions, measures, and operators against the approved catalogue.
Rejects any raw SQL or unknown members.
"""

import re
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from backend.ai_agent.metrics_catalog import (
    APPROVED_MEASURES,
    APPROVED_DIMENSIONS,
    APPROVED_MEMBERS,
    APPROVED_OPERATORS,
    APPROVED_ORDER_DIRECTIONS,
)

# Forbidden raw SQL keywords / injection patterns to prevent raw SQL injection
FORBIDDEN_SQL_PATTERN = re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|EXEC|EXECUTE|DECLARE|TRUNCATE)\b|--|;|\/\*",
    re.IGNORECASE,
)


def _check_no_sql_injection(value: Any) -> None:
    """Verifies that string values do not contain raw SQL injection patterns."""
    if isinstance(value, str):
        if FORBIDDEN_SQL_PATTERN.search(value):
            raise ValueError(
                f"Potentially unsafe raw SQL detected in value: '{value}'. Raw SQL is strictly forbidden."
            )
    elif isinstance(value, (list, tuple)):
        for item in value:
            _check_no_sql_injection(item)
    elif isinstance(value, dict):
        for k, v in value.items():
            _check_no_sql_injection(k)
            _check_no_sql_injection(v)


class CubeFilter(BaseModel):
    """
    Represents a structured semantic filter member for Cube.
    Example:
    {
        "member": "Sales.region",
        "operator": "equals",
        "values": ["Europe"]
    }
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    member: str
    operator: str
    values: List[Any] = Field(default_factory=list)

    @field_validator("member")
    @classmethod
    def validate_member(cls, v: str) -> str:
        _check_no_sql_injection(v)
        if v not in APPROVED_MEMBERS:
            raise ValueError(
                f"Unknown filter member '{v}'. Must be one of approved catalogue members: {sorted(list(APPROVED_MEMBERS))}"
            )
        return v

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        _check_no_sql_injection(v)
        if v not in APPROVED_OPERATORS:
            raise ValueError(
                f"Unsupported filter operator '{v}'. Must be one of: {sorted(list(APPROVED_OPERATORS))}"
            )
        return v

    @field_validator("values")
    @classmethod
    def validate_values(cls, v: List[Any]) -> List[Any]:
        _check_no_sql_injection(v)
        return v


class CubeTimeDimension(BaseModel):
    """
    Represents a temporal dimension slice or granularity.
    Example:
    {
        "dimension": "Sales.orderDate",
        "dateRange": ["2025-01-01", "2025-06-30"],
        "granularity": "month"
    }
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    dimension: str = "Sales.orderDate"
    dateRange: Optional[Union[List[str], str]] = None
    granularity: Optional[Literal["day", "week", "month", "quarter", "year"]] = None

    @field_validator("dimension")
    @classmethod
    def validate_dimension(cls, v: str) -> str:
        _check_no_sql_injection(v)
        if v != "Sales.orderDate":
            raise ValueError(
                f"Unsupported time dimension '{v}'. Must be 'Sales.orderDate'."
            )
        return v

    @field_validator("dateRange")
    @classmethod
    def validate_date_range(cls, v: Any) -> Any:
        _check_no_sql_injection(v)
        return v


class CubeQuery(BaseModel):
    """
    Strict semantic query contract for Cube.
    Guarantees that only approved measures, dimensions, filters, and orders are queried.
    Never allows raw SQL execution.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    measures: List[str] = Field(default_factory=list)
    dimensions: List[str] = Field(default_factory=list)
    filters: List[CubeFilter] = Field(default_factory=list)
    timeDimensions: List[CubeTimeDimension] = Field(default_factory=list)
    order: Dict[str, str] = Field(default_factory=dict)
    limit: int = Field(default=20, ge=1, le=1000)

    @field_validator("measures")
    @classmethod
    def validate_measures(cls, v: List[str]) -> List[str]:
        for measure in v:
            _check_no_sql_injection(measure)
            if measure not in APPROVED_MEASURES:
                raise ValueError(
                    f"Unknown measure '{measure}'. Must be one of: {sorted(list(APPROVED_MEASURES.keys()))}"
                )
        return v

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, v: List[str]) -> List[str]:
        for dim in v:
            _check_no_sql_injection(dim)
            if dim not in APPROVED_DIMENSIONS:
                raise ValueError(
                    f"Unknown dimension '{dim}'. Must be one of: {sorted(list(APPROVED_DIMENSIONS.keys()))}"
                )
        return v

    @field_validator("order")
    @classmethod
    def validate_order(cls, v: Dict[str, str]) -> Dict[str, str]:
        for member, direction in v.items():
            _check_no_sql_injection(member)
            _check_no_sql_injection(direction)
            if member not in APPROVED_MEMBERS:
                raise ValueError(
                    f"Order member '{member}' is not an approved Cube measure or dimension."
                )
            direction_clean = direction.lower()
            if direction_clean not in APPROVED_ORDER_DIRECTIONS:
                raise ValueError(
                    f"Order direction '{direction}' must be 'asc' or 'desc'."
                )
        return v

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "CubeQuery":
        if not self.measures and not self.dimensions:
            raise ValueError(
                "A Cube query must include at least one measure or dimension."
            )
        return self

    def to_cube_payload(self) -> Dict[str, Any]:
        """
        Serializes the query contract into the exact JSON format expected by Cube REST API (/cubejs-api/v1/load).
        """
        query_dict: Dict[str, Any] = {
            "measures": self.measures,
            "dimensions": self.dimensions,
            "limit": self.limit,
        }

        if self.filters:
            query_dict["filters"] = [
                {
                    "member": f.member,
                    "operator": f.operator,
                    "values": f.values,
                }
                for f in self.filters
            ]

        if self.timeDimensions:
            query_dict["timeDimensions"] = [
                td.model_dump(exclude_none=True) for td in self.timeDimensions
            ]

        if self.order:
            query_dict["order"] = self.order

        return {"query": query_dict}
