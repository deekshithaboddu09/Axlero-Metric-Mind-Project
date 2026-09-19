# Axlero Metric Mind Project

Agentic Semantic BI Engine - Axlero Internship Project.

## Synthetic corporate dataset

This repository includes a deterministic, artificial corporate sales dataset under
`data/`. It is intended for semantic BI, dashboard, and data-quality experiments;
it contains no real people, companies, credentials, or confidential information.

### Tables and relationships

| Table | Rows (default) | Purpose and key columns |
| --- | ---: | --- |
| `departments` | 12 | Departments, divisions, offices, budgets, and employee managers. |
| `employees` | 360 | Workforce records; `department_id` references `departments`. |
| `customers` | 450 | Artificial customer accounts and segments. |
| `products` | 80 | Product catalog, category, price, and lifecycle status. |
| `orders` | 3,000 | Sales orders; customer and sales-representative foreign keys. |
| `order_items` | ~7,500 | Order lines; `order_id` and `product_id` foreign keys, quantity, discount, and calculated total. |

All tables use a stable header and UTF-8 CSV encoding. IDs are the `*_id` columns
shown above. Dates are ISO `YYYY-MM-DD`; monetary fields are USD decimal values.
Orders join to customers and employees, while order lines join orders to products.

### Generate and validate

The standard library scripts require Python 3.9+ and write to `data/` by default:

```powershell
python scripts/generate_dataset.py
python scripts/validate_dataset.py
```

Generation uses seed `20260919`, so repeated runs produce byte-for-byte identical
CSV files. Use `--seed N`, `--scale FACTOR`, and `--output-dir PATH` to create a
different deterministic dataset or a separate output directory. For example:

```powershell
python scripts/generate_dataset.py --output-dir data-small --scale 0.25 --seed 7
python scripts/validate_dataset.py --data-dir data-small
```

The validator checks every expected schema, non-empty files, primary-key
uniqueness, all foreign-key relationships, allowed statuses, ISO dates, positive
numeric values, discounts, quantities, and order-line arithmetic.

The generated CSV files are intentionally tracked so the repository is immediately
usable. Python caches and local environment/build artifacts remain ignored by
`.gitignore`.
