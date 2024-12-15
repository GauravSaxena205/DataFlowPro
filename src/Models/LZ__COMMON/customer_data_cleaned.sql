{{ config(materialized='table') }}

-- Source table: RAW_CUSTOMER_LANDING
-- Generated from cleanup configuration

WITH null_handling AS (

    SELECT *, COALESCE(age, 0) AS age
    FROM RAW_CUSTOMER_LANDING
    WHERE email IS NOT NULL

),
WITH data_validation AS (

    SELECT 
        *,
        
        (age BETWEEN 18 AND 120) AS age_valid, 
        REGEXP_LIKE(email, '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$') AS email_valid
    FROM null_handling

),
WITH data_transformation AS (

    SELECT 
        *,
        LOWER(email) AS email
    FROM data_validation

),
WITH deduplication AS (

    WITH ranked_data AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY email ORDER BY CURRENT_TIMESTAMP) AS row_num
        FROM data_transformation
    )
    SELECT * 
    FROM ranked_data
    WHERE row_num = 1

),
final AS (
    SELECT * FROM deduplication
)

SELECT * FROM final