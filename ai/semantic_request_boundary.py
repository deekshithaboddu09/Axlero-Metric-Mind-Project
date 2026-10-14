"""
Controlled AI-to-Semantic request validation boundary.

This module validates requests only. It does not execute SQL,
calculate business metrics, or call the Cube API.
"""

from typing import Any


APPROVED_MEASURES = {
    "total orders",
    "total revenue",
    "total cost",
    "total margin",
    "total quantity",
}

APPROVED_DIMENSIONS = {
    "order_date",
    "quarter",
    "country",
    "region",
    "product_id",
    "product_name",
    "category",
    "customer_id",
}

APPROVED_FILTER_OPERATORS = {
    "equals",
    "not_equals",
    "in",
    "not_in",
    "gt",
    "gte",
    "lt",
    "lte",
}


def validate_request(request: Any) -> dict:
    """Return a structured validation result without executing a query."""

    if not isinstance(request, dict):
        return {
            "status": "error",
            "errors": ["Request must be a dictionary/object."],
        }

    errors = []

    question = request.get("question")
    measure = request.get("measure")
    dimensions = request.get("dimensions", [])
    filters = request.get("filters", [])

    if not isinstance(question, str) or not question.strip():
        errors.append("A non-empty question is required.")

    if not isinstance(measure, str) or not measure.strip():
        errors.append("A measure is required.")
    elif measure.strip().lower() not in APPROVED_MEASURES:
        errors.append(f"Unsupported measure: {measure}")

    if not isinstance(dimensions, list):
        errors.append("Dimensions must be a list.")
    else:
        for dimension in dimensions:
            if not isinstance(dimension, str):
                errors.append("Each dimension must be a string.")
            elif dimension not in APPROVED_DIMENSIONS:
                errors.append(f"Unsupported dimension: {dimension}")

        if len(dimensions) != len(set(dimensions)):
            errors.append("Duplicate dimensions are not allowed.")

    if not isinstance(filters, list):
        errors.append("Filters must be a list.")
    else:
        for index, item in enumerate(filters):
            if not isinstance(item, dict):
                errors.append(f"Filter {index}: must be an object.")
                continue

            dimension = item.get("dimension")
            operator = item.get("operator")
            value = item.get("value")

            if not isinstance(dimension, str) or dimension not in APPROVED_DIMENSIONS:
                errors.append(
                    f"Filter {index}: unsupported or missing dimension."
                )

            if not isinstance(operator, str) or operator not in APPROVED_FILTER_OPERATORS:
                errors.append(
                    f"Filter {index}: unsupported or missing operator."
                )

            if value is None or value == "":
                errors.append(f"Filter {index}: a value is required.")

    if errors:
        return {
            "status": "error",
            "errors": errors,
        }

    return {
        "status": "valid",
        "errors": [],
        "semantic_request": {
            "question": question.strip(),
            "measure": measure.strip().lower(),
            "dimensions": dimensions.copy(),
            "filters": [item.copy() for item in filters],
        },
    }