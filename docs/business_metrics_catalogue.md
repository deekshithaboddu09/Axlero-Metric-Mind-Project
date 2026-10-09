# Business Metrics Catalogue

## 1. Approved Business Metrics

| Metric | Source field | Meaning | Allowed analysis |
|---|---|---|---|
| Total Orders | COUNT(*) | Number of sales orders | region, country, category, product, quarter |
| Total Revenue | SUM(revenue) | Total sales revenue | region, country, category, product, quarter |
| Total Cost | SUM(total_cost) | Total cost | region, country, category, product, quarter |
| Total Margin | SUM(margin) | Total margin | region, country, category, product, quarter |
| Total Quantity | SUM(quantity) | Total quantity sold | region, country, category, product, quarter |
## 2. Business Rules

1. Use revenue for Revenue. Do not create another revenue formula.
2. Use total_cost for Cost.
3. Use margin for Margin.
4. Use quantity for Total Quantity.
5. Use order count for Total Orders.
6. Use approved dimensions for filtering and grouping.
7. The AI agent should not invent business formulas when a governed measure already exists.
## Business Rules

- Use revenue for Revenue. Do not create another revenue formula.
- Use total_cost for Cost.
- Use margin for Margin.
- Use quantity for Total Quantity.
- Use order count for Total Orders.
- Use approved dimensions for filtering and grouping.
- The AI agent should not invent business formulas when a governed measure already exists.
## Standard Business Questions

1. What is the total revenue?
2. What is the total cost?
3. What is the total margin?
4. How many orders do we have?
5. What is the total quantity sold?
6. What is the revenue by region?
7. What is the revenue by country?
8. What is the revenue by quarter?
9. What is the margin by region?
10. What is the margin by category?
11. What is the revenue for Europe?
12. What is the margin for Europe in Q1?