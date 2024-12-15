import os
import json
import logging

MODELS_CONFIG_PATH= 'C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\configs\\models_configs\\LZ__COMMON__CONFIG'
DBT_MODELS_PATH = 'C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\src\\Models\\LZ__COMMON'

class DBTModelGenerator:
    def __init__(self, config):
        self.config = config
        self.model_name = config.get('model_name', 'unknown_model')
        self.source_table = config.get('source_table', 'raw_source')
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _generate_cleanup_ctes(self):
        """
        Generate Common Table Expressions (CTEs) for various cleanup steps
        """
        ctes = []
        cleanup_steps = self.config.get('cleanup_steps', [])

        # Null Handling CTE
        null_handling_steps = [step for step in cleanup_steps if step['type'] == 'null_handling']
        if null_handling_steps:
            null_columns = null_handling_steps[0].get('columns', [])
            null_handling_sql = self._generate_null_handling_cte(null_columns)
            ctes.append(("null_handling", null_handling_sql))

        # Data Validation CTE
        validation_steps = [step for step in cleanup_steps if step['type'] == 'data_validation']
        if validation_steps:
            validation_checks = validation_steps[0].get('checks', [])
            validation_sql = self._generate_validation_cte(validation_checks)
            ctes.append(("data_validation", validation_sql))

        # Data Transformation CTE
        transformation_steps = [step for step in cleanup_steps if step['type'] == 'data_transformation']
        if transformation_steps:
            transformations = transformation_steps[0].get('transformations', [])
            transformation_sql = self._generate_transformation_cte(transformations)
            ctes.append(("data_transformation", transformation_sql))

        # Deduplication CTE
        dedup_steps = [step for step in cleanup_steps if step['type'] == 'deduplication']
        if dedup_steps:
            dedup_sql = self._generate_deduplication_cte(dedup_steps[0])
            ctes.append(("deduplication", dedup_sql))

        return ctes

    def _generate_null_handling_cte(self, null_columns):
        """
        Generate SQL for handling null values
        """
        if not null_columns:
            return f"SELECT * FROM {self.source_table}"

        conditions = []
        column_selects = []
        for col in null_columns:
            column = col['column_name']
            strategy = col['strategy']
            
            if strategy == 'drop_row':
                conditions.append(f"{column} IS NOT NULL")
            
            if strategy == 'replace_null':
                value = col.get('value', 'NULL')
                column_selects.append(f"COALESCE({column}, {value}) AS {column}")
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        additional_columns = f", {', '.join(column_selects)}" if column_selects else ""
        
        return f"""
    SELECT *{additional_columns}
    FROM {self.source_table}
    {where_clause}
"""

    def _generate_validation_cte(self, checks):
        """
        Generate SQL for data validation
        """
        if not checks:
            return "SELECT * FROM null_handling"

        validation_conditions = []
        for check in checks:
            column = check['column_name']
            val_type = check['validation_type']
            
            if val_type == 'range':
                min_val = check.get('min_value', 'NULL')
                max_val = check.get('max_value', 'NULL')
                validation_conditions.append(f"""
        ({column} BETWEEN {min_val} AND {max_val}) AS {column}_valid""")
            
            elif val_type == 'regex':
                regex = check.get('regex_pattern', '')
                validation_conditions.append(f"""
        REGEXP_LIKE({column}, '{regex}') AS {column}_valid""")
        
        return f"""
    SELECT 
        *,
        {', '.join(validation_conditions)}
    FROM null_handling
"""

    def _generate_transformation_cte(self, transformations):
        """
        Generate SQL for data transformations
        """
        if not transformations:
            return "SELECT * FROM data_validation"

        transform_columns = []
        for transform in transformations:
            column = transform['column_name']
            operation = transform['operation']
            
            if operation == 'trim':
                transform_columns.append(f"TRIM({column}) AS {column}")
            elif operation == 'lowercase':
                transform_columns.append(f"LOWER({column}) AS {column}")
            elif operation == 'uppercase':
                transform_columns.append(f"UPPER({column}) AS {column}")
            elif operation == 'convert_type':
                target_type = transform.get('target_type', 'STRING')
                transform_columns.append(f"CAST({column} AS {target_type}) AS {column}")
        
        return f"""
    SELECT 
        *,
        {', '.join(transform_columns)}
    FROM data_validation
"""

    def _generate_deduplication_cte(self, dedup_config):
        """
        Generate SQL for deduplication
        """
        strategy = dedup_config.get('strategy', 'keep_first')
        unique_columns = dedup_config.get('unique_columns', [])
        
        if not unique_columns:
            return "SELECT * FROM data_transformation"
        
        window_spec = f"ROW_NUMBER() OVER (PARTITION BY {', '.join(unique_columns)} ORDER BY CURRENT_TIMESTAMP)"
        
        return f"""
    WITH ranked_data AS (
        SELECT 
            *,
            {window_spec} AS row_num
        FROM data_transformation
    )
    SELECT * 
    FROM ranked_data
    WHERE row_num = 1
"""

    def generate_dbt_model(self):
        """
        Generate a complete dbt model SQL file
        """
        try:
            # Generate cleanup CTEs
            ctes = self._generate_cleanup_ctes()

            # If no CTEs were generated, use source table directly
            if not ctes:
                self.logger.warning(f"No cleanup steps found for {self.model_name}. Using source table directly.")
                model_sql = f"""{{{{ config(materialized='table') }}}}

-- Source table: {self.source_table}
-- No cleanup steps applied

SELECT * FROM {self.source_table}"""
            else:
                # Construct the full SQL
                model_sql = f"""{{{{ config(materialized='table') }}}}

-- Source table: {self.source_table}
-- Generated from cleanup configuration

"""
                
                # Add CTEs
                for name, cte_sql in ctes:
                    model_sql += f"""WITH {name} AS (
{cte_sql}
),
"""

                # Final SELECT
                model_sql += f"""final AS (
    SELECT * FROM {ctes[-1][0]}
)

SELECT * FROM final"""

            # Write to dbt model file
            output_dir = DBT_MODELS_PATH
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{self.model_name}_cleaned.sql"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(model_sql)
            
            self.logger.info(f"Generated dbt model for {self.model_name} at {filepath}")
            return model_sql

        except Exception as e:
            self.logger.error(f"Error generating dbt model for {self.model_name}: {str(e)}")
            raise

def load_json_configs(config_dir):
    """
    Loads all JSON configuration files from a given directory.

    Args:
        config_dir: The path to the directory containing the JSON files.

    Returns:
        A list of dictionaries, each representing the contents of a JSON file.
    """
    configs = []
    for root, _, files in os.walk(config_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    configs.append(config)
    return configs

def main():
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    try:
        # Load configurations
        config_files = load_json_configs(MODELS_CONFIG_PATH) 
        
        # Generate dbt models for each configuration
        for config_file in config_files:
            generator = DBTModelGenerator(config_file)
            generator.generate_dbt_model()
    
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")

if __name__ == '__main__':
    main()