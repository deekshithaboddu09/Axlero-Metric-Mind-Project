SELECT
    country,
    region
FROM {{ source('metricmind', 'geography') }}