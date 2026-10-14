# MetricMind Synthetic Dataset Documentation

## 1. Dataset Overview

MetricMind uses a synthetic corporate dataset for analytics and semantic BI.

The dataset is artificially generated using Python and is designed to support:
- Revenue analysis
- Cost analysis
- Margin analysis
- Time-based analysis
- Geography-based analysis

## 2. Dataset Files

### raw_sales.csv
Contains sales transaction information.

Columns:
- order_id
- customer_id
- product_id
- order_date
- quantity
- unit_price
- revenue
- quarter

Records: 1,000

### raw_costs.csv
Contains cost information for each sales order.

Columns:
- order_id
- material_cost
- shipping_cost

Records: 1,000

### raw_customers.csv
Contains customer information.

Columns:
- customer_id
- country

Records: 100

### raw_geography.csv
Contains country and regional information.

Columns:
- country
- region

Records: 10

### raw_products.csv
Contains product information.

Columns:
- product_id
- product_name
- category
- list_price

Records: 5

## 3. Relationships

- raw_sales.customer_id → raw_customers.customer_id
- raw_sales.product_id → raw_products.product_id
- raw_sales.order_id → raw_costs.order_id
- raw_customers.country → raw_geography.country

## 4. Metric Mapping

### Revenue
Revenue is taken from the `revenue` column in raw_sales.csv.

### Cost
Total cost can be calculated using:
- material_cost
- shipping_cost

from raw_costs.csv.

### Margin
Margin can be calculated as:

Margin = Revenue - Total Cost

### Time
Time analysis uses:
- order_date
- quarter

from raw_sales.csv.

### Geography
Geography analysis uses:
- country
- region

from raw_customers.csv and raw_geography.csv.

## 5. Data Generation

The synthetic dataset was generated using:

`data/generate_mock_data.py`

The generated CSV files are stored in:

`data/raw/`