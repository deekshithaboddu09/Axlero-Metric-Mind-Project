"""
MetricMind Semantic Metrics Catalogue
Defines approved Cube measures, dimensions, descriptions, and valid operators.
All members match cube/model/cubes/Sales.js.
"""

from typing import Any, Dict

# Approved Measures defined in Sales.js
APPROVED_MEASURES: Dict[str, Dict[str, Any]] = {
    "Sales.totalRevenue": {
        "title": "Total Revenue",
        "description": "Sum of transaction revenue in USD ($).",
        "type": "number",
        "format": "currency",
        "sql_field": "revenue",
    },
    "Sales.totalCost": {
        "title": "Total Cost",
        "description": "Sum of total costs (material cost + shipping cost) in USD ($).",
        "type": "number",
        "format": "currency",
        "sql_field": "total_cost",
    },
    "Sales.totalMargin": {
        "title": "Total Margin",
        "description": "Sum of gross margin (revenue - total cost) in USD ($).",
        "type": "number",
        "format": "currency",
        "sql_field": "margin",
    },
    "Sales.totalOrders": {
        "title": "Total Orders",
        "description": "Count of distinct orders (unique order_id).",
        "type": "number",
        "format": "integer",
        "sql_field": "order_id",
    },
    "Sales.totalQuantity": {
        "title": "Total Quantity",
        "description": "Sum of units of product purchased across orders.",
        "type": "number",
        "format": "integer",
        "sql_field": "quantity",
    },
    "Sales.averageOrderValue": {
        "title": "Average Order Value",
        "description": "Total revenue divided by total orders (AOV in $). Safe from division by zero.",
        "type": "number",
        "format": "currency",
        "calculated": True,
    },
    "Sales.marginRate": {
        "title": "Margin Rate",
        "description": "Ratio of total margin to total revenue (margin %). Safe from division by zero.",
        "type": "number",
        "format": "percentage",
        "calculated": True,
    },
}

# Approved Dimensions defined in Sales.js
APPROVED_DIMENSIONS: Dict[str, Dict[str, Any]] = {
    "Sales.orderId": {
        "title": "Order ID",
        "description": "Unique identifier for each sales order (primary key).",
        "type": "string",
    },
    "Sales.orderDate": {
        "title": "Order Date",
        "description": "Date when the order occurred (temporal dimension).",
        "type": "time",
    },
    "Sales.quarter": {
        "title": "Quarter",
        "description": "Fiscal quarter of the order.",
        "type": "string",
        "allowed_values": ["Q1", "Q2", "Q3", "Q4"],
    },
    "Sales.region": {
        "title": "Region",
        "description": "Geographic macro-region.",
        "type": "string",
        "allowed_values": ["APAC", "Europe", "North America"],
    },
    "Sales.country": {
        "title": "Country",
        "description": "Country where the customer is located.",
        "type": "string",
        "allowed_values": [
            "Australia",
            "Canada",
            "France",
            "Germany",
            "India",
            "Japan",
            "Singapore",
            "Spain",
            "United Kingdom",
            "United States",
        ],
    },
    "Sales.productName": {
        "title": "Product Name",
        "description": "Name of the product sold.",
        "type": "string",
        "allowed_values": [
            "Analytics Suite",
            "BI Connector",
            "Data Pipeline Kit",
            "Edge Sensor Pack",
            "Support Plan",
        ],
    },
    "Sales.category": {
        "title": "Category",
        "description": "Product classification category.",
        "type": "string",
        "allowed_values": ["Hardware", "Services", "Software"],
    },
    "Sales.customerId": {
        "title": "Customer ID",
        "description": "Unique identifier for the ordering customer.",
        "type": "string",
    },
}

# Approved Filter Operators
APPROVED_OPERATORS = {
    "equals",
    "notEquals",
    "contains",
    "notContains",
    "gt",
    "gte",
    "lt",
    "lte",
    "set",
    "notSet",
    "inDateRange",
}

# Approved Order Directions
APPROVED_ORDER_DIRECTIONS = {"asc", "desc"}

# All approved members (Measures + Dimensions)
APPROVED_MEMBERS = set(APPROVED_MEASURES.keys()) | set(APPROVED_DIMENSIONS.keys())

# Complete Metrics Catalog metadata
METRICS_CATALOG = {
    "cube_name": "Sales",
    "measures": APPROVED_MEASURES,
    "dimensions": APPROVED_DIMENSIONS,
    "operators": sorted(list(APPROVED_OPERATORS)),
    "order_directions": sorted(list(APPROVED_ORDER_DIRECTIONS)),
}


def get_catalog_prompt_context() -> str:
    """
    Generates a structured prompt string documenting the catalogue for LLM agents.
    Provides strict guidelines to prevent raw SQL or hallucinated member names.
    """
    lines = [
        "### METRICMIND SEMANTIC METRICS CATALOGUE",
        "",
        "You are an AI analyst that translates user business questions into structured Cube queries.",
        "CRITICAL RULE: You must ONLY use the approved measures and dimensions listed below.",
        "NEVER generate raw SQL, table names, or unlisted column names.",
        "",
        "#### APPROVED MEASURES (Numeric aggregations):",
    ]

    for member, meta in APPROVED_MEASURES.items():
        lines.append(f"- `{member}`: {meta['description']}")

    lines.append("")
    lines.append("#### APPROVED DIMENSIONS (Grouping and filtering):")

    for member, meta in APPROVED_DIMENSIONS.items():
        val_str = ""
        if "allowed_values" in meta:
            val_str = f" Valid values: {meta['allowed_values']}."
        lines.append(f"- `{member}` ({meta['type']}): {meta['description']}{val_str}")

    lines.append("")
    lines.append("#### APPROVED FILTER OPERATORS:")
    lines.append(
        "- `equals`, `notEquals`, `contains`, `notContains`, `gt`, `gte`, `lt`, `lte`, `set`, `notSet`, `inDateRange`"
    )

    lines.append("")
    lines.append("#### QUERY STRUCTURE RULES:")
    lines.append("1. Always specify at least one measure (e.g. ['Sales.totalRevenue']).")
    lines.append("2. Add dimensions when grouping (e.g. ['Sales.quarter'] or ['Sales.country']).")
    lines.append("3. For 'highest' / 'top' questions: order by the measure 'desc', limit 1.")
    lines.append("4. For 'lowest' / 'bottom' questions: order by the measure 'asc', limit 1.")
    lines.append("5. Set a safe limit between 1 and 1000 (default: 20).")

    return "\n".join(lines)
