SELECT
    order_id,
    material_cost,
    shipping_cost
FROM {{ source('metricmind', 'costs') }}