SELECT
    s.order_id,
    s.order_date,
    s.customer_id,
    c.country,
    g.region,
    s.product_id,
    p.product_name,
    p.category,
    s.quantity,
    s.unit_price,
    s.revenue,
    co.material_cost,
    co.shipping_cost,
    (co.material_cost + co.shipping_cost) AS total_cost,
    (s.revenue - co.material_cost - co.shipping_cost) AS margin,
    s.quarter
FROM {{ ref('stg_sales') }} s
LEFT JOIN {{ ref('stg_customers') }} c
    ON s.customer_id = c.customer_id
LEFT JOIN {{ ref('stg_geography') }} g
    ON c.country = g.country
LEFT JOIN {{ ref('stg_products') }} p
    ON s.product_id = p.product_id
LEFT JOIN {{ ref('stg_costs') }} co
    ON s.order_id = co.order_id