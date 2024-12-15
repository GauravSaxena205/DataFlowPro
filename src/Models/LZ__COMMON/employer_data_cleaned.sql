{{ config(materialized='table') }}

-- Source table: RAW_EMPLOYER_LANDING
-- Generated from cleanup configuration

WITH null_handling AS (

    SELECT *, COALESCE(employee_count, 0) AS employee_count, COALESCE(industry, Unknown) AS industry
    FROM RAW_EMPLOYER_LANDING
    WHERE company_name IS NOT NULL

),
WITH data_validation AS (

    SELECT 
        *,
        
        (employee_count BETWEEN 0 AND 1000000) AS employee_count_valid, 
        REGEXP_LIKE(company_website, '^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})[/\w \.-]*/?$') AS company_website_valid, 
        (founding_year BETWEEN 1600 AND 2024) AS founding_year_valid
    FROM null_handling

),
WITH data_transformation AS (

    SELECT 
        *,
        TRIM(company_name) AS company_name, UPPER(industry) AS industry, CAST(founding_year AS integer) AS founding_year
    FROM data_validation

),
WITH deduplication AS (

    WITH ranked_data AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY company_name, tax_id ORDER BY CURRENT_TIMESTAMP) AS row_num
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