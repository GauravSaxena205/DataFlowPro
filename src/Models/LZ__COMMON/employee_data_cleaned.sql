{{ config(materialized='table') }}

-- Source table: RAW_EMPLOYEE_LANDING
-- Generated from cleanup configuration

WITH null_handling AS (

    SELECT *, COALESCE(first_name, Unknown) AS first_name, COALESCE(last_name, Unknown) AS last_name, COALESCE(salary, 0) AS salary, COALESCE(department, Unassigned) AS department
    FROM RAW_EMPLOYEE_LANDING
    WHERE employee_id IS NOT NULL

),
WITH data_validation AS (

    SELECT 
        *,
        
        REGEXP_LIKE(employee_id, '^[A-Z]{2}\d{6}$') AS employee_id_valid, 
        REGEXP_LIKE(email, '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$') AS email_valid, 
        (age BETWEEN 18 AND 85) AS age_valid, 
        (salary BETWEEN 0 AND 1000000) AS salary_valid, 
        (hire_date BETWEEN 1990-01-01 AND 2024-12-31) AS hire_date_valid
    FROM null_handling

),
WITH data_transformation AS (

    SELECT 
        *,
        TRIM(first_name) AS first_name, TRIM(last_name) AS last_name, LOWER(email) AS email, CAST(hire_date AS date) AS hire_date, UPPER(department) AS department
    FROM data_validation

),
WITH deduplication AS (

    WITH ranked_data AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY employee_id, email ORDER BY CURRENT_TIMESTAMP) AS row_num
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