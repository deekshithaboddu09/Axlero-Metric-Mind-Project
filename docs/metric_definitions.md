# Metric Definitions

## Time
Used to analyse data by date, month, quarter or year.

## Geography
Used to analyse data by country, region, city or other location.

## Revenue
Total sales/revenue value used for business analysis.

## Cost
Cost associated with the business activity.

## Margin
Profitability metric based on revenue and cost.

## Confirmed Field Mappings

| Semantic item | Confirmed field | Meaning |
|---|---|---|
| Time | order_date | Date used for time analysis |
| Time | quarter | Quarter used for quarterly analysis |
| Geography | country | Country-level analysis |
| Geography | region | Region-level analysis |
| Revenue | revenue | Total revenue |
| Cost | total_cost | Total cost |
| Margin | margin | Revenue minus material cost and shipping cost |
# Business Metrics Catalogue

| Metric | Source field | Meaning | Allowed analysis |
|---|---|---|---|
| Total Orders | COUNT(*) | Number of sales orders | region, country, category, product, quarter |
| Total Revenue | SUM(revenue) | Total sales revenue | region, country, category, product, quarter |
| Total Cost | SUM(total_cost) | Total cost | region, country, category, product, quarter |
| Total Margin | SUM(margin) | Total margin | region, country, category, product, quarter |
| Total Quantity | SUM(quantity) | Total quantity sold | region, country, category, product, quarter |