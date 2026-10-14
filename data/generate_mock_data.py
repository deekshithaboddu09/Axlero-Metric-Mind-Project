import os
import random
from datetime import date, timedelta
import pandas as pd

random.seed(42)

# Current data folder
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")

# Create raw folder if it does not exist
os.makedirs(RAW, exist_ok=True)


# 1. GEOGRAPHY DATA
geography = [
    ("Germany", "Europe"),
    ("France", "Europe"),
    ("UK", "Europe"),
    ("Spain", "Europe"),
    ("Italy", "Europe"),
    ("USA", "North America"),
    ("Canada", "North America"),
    ("Japan", "APAC"),
    ("Australia", "APAC"),
    ("Singapore", "APAC")
]

pd.DataFrame(
    geography,
    columns=["country", "region"]
).to_csv(
    os.path.join(RAW, "raw_geography.csv"),
    index=False
)


# 2. CUSTOMER DATA
countries = [country for country, region in geography]

customers = []

for i in range(1, 101):
    customer_id = f"C-{i:04d}"
    country = random.choice(countries)
    customers.append([customer_id, country])

pd.DataFrame(
    customers,
    columns=["customer_id", "country"]
).to_csv(
    os.path.join(RAW, "raw_customers.csv"),
    index=False
)


# 3. PRODUCT DATA
products = [
    ("P-100", "Analytics Suite", "Software", 1200),
    ("P-101", "BI Connector", "Software", 400),
    ("P-102", "Data Pipeline Kit", "Hardware", 800),
    ("P-103", "Edge Sensor Pack", "Hardware", 250),
    ("P-104", "Support Plan", "Services", 150)
]

pd.DataFrame(
    products,
    columns=["product_id", "product_name", "category", "list_price"]
).to_csv(
    os.path.join(RAW, "raw_products.csv"),
    index=False
)


# 4. SALES DATA
sales = []

start_date = date(2025, 1, 1)

for i in range(1, 1001):

    order_id = f"O-{i:05d}"

    customer_id = random.choice(customers)[0]

    product = random.choice(products)

    product_id = product[0]
    list_price = product[3]

    order_date = start_date + timedelta(
        days=random.randint(0, 364)
    )

    quantity = random.randint(1, 20)

    unit_price = round(
        list_price * random.uniform(0.80, 1.15),
        2
    )

    revenue = round(
        quantity * unit_price,
        2
    )

    quarter = f"Q{((order_date.month - 1) // 3) + 1}"

    sales.append([
        order_id,
        customer_id,
        product_id,
        order_date.isoformat(),
        quantity,
        unit_price,
        revenue,
        quarter
    ])


pd.DataFrame(
    sales,
    columns=[
        "order_id",
        "customer_id",
        "product_id",
        "order_date",
        "quantity",
        "unit_price",
        "revenue",
        "quarter"
    ]
).to_csv(
    os.path.join(RAW, "raw_sales.csv"),
    index=False
)


# 5. COST DATA
costs = []

for sale in sales:

    order_id = sale[0]
    revenue = sale[6]

    material_cost = round(
        revenue * random.uniform(0.15, 0.45),
        2
    )

    shipping_cost = round(
        revenue * random.uniform(0.03, 0.12),
        2
    )

    costs.append([
        order_id,
        material_cost,
        shipping_cost
    ])


pd.DataFrame(
    costs,
    columns=[
        "order_id",
        "material_cost",
        "shipping_cost"
    ]
).to_csv(
    os.path.join(RAW, "raw_costs.csv"),
    index=False
)


print("Synthetic dataset created successfully!")
print("Files saved in:", RAW)