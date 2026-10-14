SELECT
    product_id,
    product_name,
    category,
    list_price
FROM {{ source('metricmind', 'products') }}