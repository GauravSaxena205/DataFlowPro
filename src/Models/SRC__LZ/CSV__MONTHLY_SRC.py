import pandas as pd
import snowflake.connector

def load_csv_to_snowflake(config):
    """
    Loads data from a CSV file into a Snowflake table.

    Args:
        config (dict): A dictionary containing the following keys:
            - file_location (str): The path to the CSV file.
            - snowflake_db (str): The Snowflake database name.
            - snowflake_schema (str): The Snowflake schema name.
            - snowflake_table (str): The Snowflake table name.
            - snowflake_user (str): Your Snowflake username.
            - snowflake_password (str): Your Snowflake password.
            - snowflake_account (str): Your Snowflake account identifier.
            - snowflake_warehouse (str): Your Snowflake warehouse.

    Raises:
        FileNotFoundError: If the CSV file is not found.
        snowflake.connector.errors.ProgrammingError: If there's an error during Snowflake interaction.
        KeyError: If any required key is missing from the config dictionary.
    """
    required_keys = [
        'file_location', 'snowflake_db', 'snowflake_schema', 'snowflake_table',
        'snowflake_user', 'snowflake_password', 'snowflake_account', 'snowflake_warehouse'
    ]
    missing_keys = set(required_keys) - set(config.keys())
    if missing_keys:
        raise KeyError(f"Missing required keys in config: {missing_keys}")

    try:
        # Load CSV into pandas DataFrame
        df = pd.read_csv(config['file_location'])

        # Establish Snowflake connection
        conn = snowflake.connector.connect(
            user=config['snowflake_user'],
            password=config['snowflake_password'],
            account=config['snowflake_account'],
            warehouse=config['snowflake_warehouse'],
            database=config['snowflake_db'],
            schema=config['snowflake_schema']
        )

        cur = conn.cursor()

        # Create a temporary stage in Snowflake to upload the data
        stage_name = "my_stage"  # You might want to make this dynamic to avoid conflicts
        create_stage_sql = f"CREATE OR REPLACE STAGE {stage_name}"
        cur.execute(create_stage_sql)

        # Put the CSV file into the stage
        cur.execute(f"PUT file://{config['file_location']} @{stage_name}")

        # Copy data from stage to table. Adjust the copy command based on your CSV format.
        copy_sql = f"""
            COPY INTO {config['snowflake_table']}
            FROM @{stage_name}/{config['file_location'].split('/')[-1]}
            FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = ',' HEADER = TRUE)
        """
        cur.execute(copy_sql)
        conn.commit()

        print(f"Data successfully loaded into {config['snowflake_db']}.{config['snowflake_schema']}.{config['snowflake_table']}")

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at: {config['file_location']}")
    except snowflake.connector.errors.ProgrammingError as e:
        raise snowflake.connector.errors.ProgrammingError(f"Snowflake error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# Example usage (Remember to replace with your actual credentials and file path):
config = {
    'file_location': '/path/to/your/file.csv',  # Replace with your CSV file path
    'snowflake_db': 'your_database',
    'snowflake_schema': 'your_schema',
    'snowflake_table': 'your_table',
    'snowflake_user': 'your_username',
    'snowflake_password': 'your_password',
    'snowflake_account': 'your_account',
    'snowflake_warehouse': 'your_warehouse'
}

load_csv_to_snowflake(config)
