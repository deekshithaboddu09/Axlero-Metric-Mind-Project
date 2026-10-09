# Semantic Layer Test Results

| Business Question | Status | Notes |
|---|---|---|
| What is the revenue for Europe? | PENDING | Cube test pending |
| What is the margin for Europe in Q1? | PENDING | Cube test pending |
| What is the revenue by region? | PENDING | Cube test pending |
| What is the margin by category? | PENDING | Cube test pending |
| What is the revenue by quarter? | PENDING | Cube test pending |
## Question to Semantic Mapping

| Business question | Measure | Dimension | Filter |
|---|---|---|---|
| What is the total revenue? | total revenue | None | None |
| What is the revenue by region? | total revenue | region | None |
| What is the revenue by quarter? | total revenue | quarter | None |
| What is the margin by region? | total margin | region | None |
| What is the margin by category? | total margin | category | None |
| What is the revenue for Europe? | total revenue | None | region = Europe |
| What is the margin for Europe in Q1? | total margin | None | region = Europe AND quarter = Q1 |
## Supported Filter Combinations

- region + measure
- country + measure
- category + measure
- product_name + measure
- quarter + measure
- region + quarter + measure
- country + category + measure

Only dimensions already present in the approved model should be used.