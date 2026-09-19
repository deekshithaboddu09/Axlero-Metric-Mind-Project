#!/usr/bin/env python3
"""Generate a deterministic synthetic corporate sales dataset."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

DEFAULT_SEED = 20260919
START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)

DEPARTMENTS = [
    ("D001", "Executive", "Corporate", "New York"),
    ("D002", "Finance", "Corporate", "New York"),
    ("D003", "Human Resources", "Corporate", "Chicago"),
    ("D004", "Sales", "Revenue", "Chicago"),
    ("D005", "Marketing", "Revenue", "Austin"),
    ("D006", "Customer Success", "Revenue", "Austin"),
    ("D007", "Engineering", "Technology", "Seattle"),
    ("D008", "Data & Analytics", "Technology", "Seattle"),
    ("D009", "Product", "Technology", "San Francisco"),
    ("D010", "Operations", "Operations", "Dallas"),
    ("D011", "Legal", "Corporate", "New York"),
    ("D012", "Procurement", "Operations", "Dallas"),
]
FIRST_NAMES = ["Avery", "Blake", "Casey", "Devon", "Emery", "Finley", "Jordan", "Kai", "Logan", "Morgan", "Parker", "Quinn", "Reese", "Riley", "Rowan", "Sawyer", "Skyler", "Taylor", "Terry", "Wesley"]
LAST_NAMES = ["Adams", "Bennett", "Carter", "Dawson", "Ellis", "Foster", "Grant", "Hayes", "Irwin", "Jenkins", "Kim", "Lopez", "Morris", "Nguyen", "Owens", "Patel", "Reed", "Shaw", "Turner", "Vega"]
COMPANIES = ["Northstar", "BluePeak", "CedarWorks", "Cloudline", "Evergreen", "HarborPoint", "Ironwood", "Lumen", "Pioneer", "Redwood", "Summit", "Westbridge"]
CITIES = ["Austin", "Boston", "Chicago", "Dallas", "Denver", "New York", "Phoenix", "Portland", "San Diego", "Seattle"]
PRODUCTS = [
    ("Analytics", ["Insight", "Forecast", "Signal", "Metric", "Pulse"]),
    ("Collaboration", ["Connect", "Workspace", "Relay", "Circle", "Canvas"]),
    ("Security", ["Guard", "Shield", "Vault", "Sentinel", "Trust"]),
    ("Infrastructure", ["Compute", "Storage", "Network", "Deploy", "Scale"]),
]


def iso_day(rng: random.Random) -> str:
    days = (END_DATE - START_DATE).days
    return (START_DATE + timedelta(days=rng.randint(0, days))).isoformat()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generate(output_dir: Path, seed: int = DEFAULT_SEED, scale: float = 1.0) -> dict[str, int]:
    if scale <= 0:
        raise ValueError("scale must be greater than zero")
    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    departments = [
        {"department_id": dep_id, "department_name": name, "division": division, "office_city": city, "annual_budget_usd": f"{rng.randint(900, 9500) * 1000:.2f}"}
        for dep_id, name, division, city in DEPARTMENTS
    ]
    employee_count = max(12, round(360 * scale))
    employees = []
    for index in range(1, employee_count + 1):
        dep_id = DEPARTMENTS[(index * 7 + rng.randrange(len(DEPARTMENTS))) % len(DEPARTMENTS)][0]
        first = FIRST_NAMES[rng.randrange(len(FIRST_NAMES))]
        last = LAST_NAMES[rng.randrange(len(LAST_NAMES))]
        employees.append({
            "employee_id": f"E{index:05d}",
            "department_id": dep_id,
            "first_name": first,
            "last_name": last,
            "job_title": "Manager" if index <= len(DEPARTMENTS) else rng.choice(["Analyst", "Specialist", "Consultant", "Coordinator", "Senior Associate"]),
            "hire_date": (date(2015, 1, 1) + timedelta(days=rng.randint(0, 3900))).isoformat(),
            "employment_status": rng.choices(["Active", "On Leave", "Inactive"], weights=[92, 4, 4])[0],
            "annual_salary_usd": f"{rng.randint(480, 1850) * 100:.2f}",
        })
    managers = {}
    for department in departments:
        department_employees = [employee for employee in employees if employee["department_id"] == department["department_id"]]
        manager = department_employees[0]
        manager["job_title"] = "Manager"
        managers[department["department_id"]] = manager["employee_id"]
    for department in departments:
        department["manager_employee_id"] = managers[department["department_id"]]

    customer_count = max(50, round(450 * scale))
    customers = []
    for index in range(1, customer_count + 1):
        customers.append({
            "customer_id": f"C{index:05d}",
            "company_name": f"{rng.choice(COMPANIES)} {rng.choice(['Holdings', 'Group', 'Systems', 'Industries', 'Partners'])} {index:03d}",
            "industry": rng.choice(["Technology", "Healthcare", "Financial Services", "Manufacturing", "Retail", "Professional Services"]),
            "customer_segment": rng.choices(["Enterprise", "Mid-Market", "SMB"], weights=[20, 45, 35])[0],
            "billing_city": rng.choice(CITIES),
            "account_opened_date": (date(2018, 1, 1) + timedelta(days=rng.randint(0, 2500))).isoformat(),
            "customer_status": rng.choices(["Active", "At Risk", "Churned"], weights=[82, 12, 6])[0],
        })

    product_rows = []
    product_count = max(20, round(80 * scale))
    for index in range(1, product_count + 1):
        category, names = PRODUCTS[(index - 1) % len(PRODUCTS)]
        product_rows.append({
            "product_id": f"P{index:04d}",
            "product_name": f"{rng.choice(names)} {['Core', 'Plus', 'Pro', 'Enterprise'][index % 4]}",
            "category": category,
            "unit_price_usd": f"{rng.randint(25, 1800) * 10:.2f}",
            "product_status": rng.choices(["Active", "Retired"], weights=[94, 6])[0],
        })

    sales_reps = [employee["employee_id"] for employee in employees if employee["department_id"] == "D004"] or [employees[0]["employee_id"]]
    order_count = max(100, round(3000 * scale))
    orders = []
    order_items = []
    for order_number in range(1, order_count + 1):
        order_id = f"O{order_number:06d}"
        order_date = iso_day(rng)
        status = rng.choices(["Completed", "Shipped", "Processing", "Cancelled"], weights=[58, 22, 15, 5])[0]
        orders.append({
            "order_id": order_id,
            "customer_id": f"C{rng.randint(1, customer_count):05d}",
            "sales_rep_employee_id": rng.choice(sales_reps),
            "order_date": order_date,
            "order_status": status,
            "currency": "USD",
        })
        for line_number in range(1, rng.randint(1, 5) + 1):
            product = rng.choice(product_rows)
            quantity = rng.randint(1, 12)
            unit_price = float(product["unit_price_usd"])
            discount = rng.choice([0, 0, 0, 5, 10, 15])
            total = quantity * unit_price * (1 - discount / 100)
            order_items.append({
                "order_item_id": f"OI{len(order_items) + 1:07d}",
                "order_id": order_id,
                "product_id": product["product_id"],
                "line_number": line_number,
                "quantity": quantity,
                "unit_price_usd": f"{unit_price:.2f}",
                "discount_percent": f"{discount:.2f}",
                "line_total_usd": f"{total:.2f}",
            })

    tables = {
        "departments": (["department_id", "department_name", "division", "office_city", "manager_employee_id", "annual_budget_usd"], departments),
        "employees": (["employee_id", "department_id", "first_name", "last_name", "job_title", "hire_date", "employment_status", "annual_salary_usd"], employees),
        "customers": (["customer_id", "company_name", "industry", "customer_segment", "billing_city", "account_opened_date", "customer_status"], customers),
        "products": (["product_id", "product_name", "category", "unit_price_usd", "product_status"], product_rows),
        "orders": (["order_id", "customer_id", "sales_rep_employee_id", "order_date", "order_status", "currency"], orders),
        "order_items": (["order_item_id", "order_id", "product_id", "line_number", "quantity", "unit_price_usd", "discount_percent", "line_total_usd"], order_items),
    }
    for name, (fields, rows) in tables.items():
        write_csv(output_dir / f"{name}.csv", fields, rows)
    return {name: len(rows) for name, (_, rows) in tables.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()
    counts = generate(args.output_dir, args.seed, args.scale)
    print(f"Generated {len(counts)} tables in {args.output_dir} with seed {args.seed}:")
    for name, count in counts.items():
        print(f"  {name}: {count:,} rows")


if __name__ == "__main__":
    main()
