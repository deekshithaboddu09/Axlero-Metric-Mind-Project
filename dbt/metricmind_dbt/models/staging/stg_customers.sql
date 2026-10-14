SELECT
    customer_id,
    country
FROM {{ source('metricmind', 'customers') }}