{{ config(materialized='table') }}

-- Source table: RAW_FINANCIAL_LANDING
-- Generated from cleanup configuration

WITH null_handling AS (

    SELECT *, COALESCE(amount, 0) AS amount, COALESCE(account_type, Unknown) AS account_type, COALESCE(category, Miscellaneous) AS category
    FROM RAW_FINANCIAL_LANDING
    WHERE transaction_id IS NOT NULL

),
WITH data_validation AS (

    SELECT 
        *,
        
        REGEXP_LIKE(transaction_id, '^[A-Z]{2}\d{8}$') AS transaction_id_valid, 
        (amount BETWEEN -1000000 AND 1000000) AS amount_valid, 
        (transaction_date BETWEEN 2000-01-01 AND 2024-12-31) AS transaction_date_valid, 
        REGEXP_LIKE(currency, '^[A-Z]{3}$') AS currency_valid
    FROM null_handling

),
WITH data_transformation AS (

    SELECT 
        *,
        CAST(transaction_date AS date) AS transaction_date, TRIM(description) AS description, UPPER(account_type) AS account_type
    FROM data_validation

),
WITH deduplication AS (

    WITH ranked_data AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY transaction_id, transaction_date, amount ORDER BY CURRENT_TIMESTAMP) AS row_num
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