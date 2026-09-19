#!/usr/bin/env python3
"""Validate schemas, constraints, and relationships in the generated CSV data."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

EXPECTED = {
    "departments": ["department_id", "department_name", "division", "office_city", "manager_employee_id", "annual_budget_usd"],
    "employees": ["employee_id", "department_id", "first_name", "last_name", "job_title", "hire_date", "employment_status", "annual_salary_usd"],
    "customers": ["customer_id", "company_name", "industry", "customer_segment", "billing_city", "account_opened_date", "customer_status"],
    "products": ["product_id", "product_name", "category", "unit_price_usd", "product_status"],
    "orders": ["order_id", "customer_id", "sales_rep_employee_id", "order_date", "order_status", "currency"],
    "order_items": ["order_item_id", "order_id", "product_id", "line_number", "quantity", "unit_price_usd", "discount_percent", "line_total_usd"],
}
DATE_FIELDS = {"hire_date", "account_opened_date", "order_date"}


def read_table(data_dir: Path, name: str) -> list[dict[str, str]]:
    path = data_dir / f"{name}.csv"
    if not path.exists():
        raise ValueError(f"missing file: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED[name]:
            raise ValueError(f"{name}: schema is {reader.fieldnames}, expected {EXPECTED[name]}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{name}: file contains no data rows")
    return rows


def validate(data_dir: Path) -> dict[str, int]:
    tables = {name: read_table(data_dir, name) for name in EXPECTED}
    primary_keys = {"departments": "department_id", "employees": "employee_id", "customers": "customer_id", "products": "product_id", "orders": "order_id", "order_items": "order_item_id"}
    keys = {}
    for name, rows in tables.items():
        key = primary_keys[name]
        values = [row[key] for row in rows]
        if any(not value for value in values) or len(values) != len(set(values)):
            raise ValueError(f"{name}: primary key {key} is empty or duplicated")
        keys[name] = set(values)
        for row in rows:
            for field in DATE_FIELDS.intersection(row):
                try:
                    date.fromisoformat(row[field])
                except ValueError as exc:
                    raise ValueError(f"{name}: invalid ISO date in {field}: {row[field]}") from exc

    def require(table: str, field: str, parent: str) -> None:
        missing = {row[field] for row in tables[table] if row[field] not in keys[parent]}
        if missing:
            raise ValueError(f"{table}.{field}: unknown {parent} keys {sorted(missing)[:3]}")

    require("departments", "manager_employee_id", "employees")
    require("employees", "department_id", "departments")
    require("orders", "customer_id", "customers")
    require("orders", "sales_rep_employee_id", "employees")
    require("order_items", "order_id", "orders")
    require("order_items", "product_id", "products")
    employee_by_id = {row["employee_id"]: row for row in tables["employees"]}
    for department in tables["departments"]:
        if employee_by_id[department["manager_employee_id"]]["department_id"] != department["department_id"]:
            raise ValueError(f"departments {department['department_id']}: manager is outside the department")
    allowed = {
        "employees.employment_status": {"Active", "On Leave", "Inactive"},
        "customers.customer_segment": {"Enterprise", "Mid-Market", "SMB"},
        "customers.customer_status": {"Active", "At Risk", "Churned"},
        "products.product_status": {"Active", "Retired"},
        "orders.order_status": {"Completed", "Shipped", "Processing", "Cancelled"},
    }
    for qualified, values in allowed.items():
        table, field = qualified.split(".")
        invalid = {row[field] for row in tables[table] if row[field] not in values}
        if invalid:
            raise ValueError(f"{qualified}: invalid values {sorted(invalid)}")
    for name, field in [("departments", "annual_budget_usd"), ("employees", "annual_salary_usd"), ("products", "unit_price_usd"), ("order_items", "unit_price_usd"), ("order_items", "line_total_usd")]:
        if any(float(row[field]) <= 0 for row in tables[name]):
            raise ValueError(f"{name}.{field}: values must be positive")
    for row in tables["order_items"]:
        if int(row["quantity"]) <= 0 or not 0 <= float(row["discount_percent"]) <= 100:
            raise ValueError("order_items: invalid quantity or discount")
        expected_total = int(row["quantity"]) * float(row["unit_price_usd"]) * (1 - float(row["discount_percent"]) / 100)
        if abs(expected_total - float(row["line_total_usd"])) > 0.01:
            raise ValueError(f"order_items {row['order_item_id']}: incorrect line total")
    return {name: len(rows) for name, rows in tables.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    counts = validate(args.data_dir)
    print("Validation passed:")
    for name, count in counts.items():
        print(f"  {name}: {count:,} rows")


if __name__ == "__main__":
    main()
