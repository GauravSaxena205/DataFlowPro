import pandas as pd
import snowflake.connector
import logging

def load_csv_to_snowflake(config):
    """
    Loads data from a CSV file into a Snowflake table.

    Args:
        config (dict): A dictionary containing the following keys:
            - file_location (str): Path to the CSV file.
            - snowflake_db (str): Snowflake database name.
            - snowflake_schema (str): Snowflake schema name.
            - snowflake_table (str): Snowflake table name.
            - snowflake_user (str): Snowflake username. (Added for completeness)
            - snowflake_password (str): Snowflake password. (Added for completeness)
            - snowflake_account (str): Snowflake account identifier. (Added for completeness)
            - snowflake_warehouse (str): Snowflake warehouse name. (Optional, defaults to 'COMPUTE_WH')

    Returns:
        bool: True if the data was successfully loaded, False otherwise. Raises exceptions for various errors.
    """

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Check for required config keys
    required_keys = [
        'file_location', 'snowflake_db', 'snowflake_schema', 'snowflake_table',
        'snowflake_user', 'snowflake_password', 'snowflake_account'
    ]
    missing_keys = set(required_keys) - set(config.keys())
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

    file_location = config['file_location']
    snowflake_db = config['snowflake_db']
    snowflake_schema = config['snowflake_schema']
    snowflake_table = config['snowflake_table']
    snowflake_user = config['snowflake_user']
    snowflake_password = config['snowflake_password']
    snowflake_account = config['snowflake_account']
    snowflake_warehouse = config.get('snowflake_warehouse', 'COMPUTE_WH')  # Default warehouse

    try:
        # Load CSV into pandas DataFrame
        logging.info(f"Loading CSV data from: {file_location}")
        df = pd.read_csv(file_location)

        # Connect to Snowflake
        logging.info(f"Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            user=snowflake_user,
            password=snowflake_password,
            account=snowflake_account,
            warehouse=snowflake_warehouse,
            database=snowflake_db,
            schema=snowflake_schema
        )

        # Create a cursor object
        cur = conn.cursor()

        # Insert data into Snowflake table. Handles potential errors during insertion
        try:
            logging.info(f"Inserting data into table: {snowflake_db}.{snowflake_schema}.{snowflake_table}")
            for index, row in df.iterrows():
                # Construct the INSERT statement dynamically to avoid SQL injection vulnerability.
                columns = ', '.join(df.columns)
                values = ', '.join('%s' * len(df.columns))
                query = f"INSERT INTO {snowflake_db}.{snowflake_schema}.{snowflake_table} ({columns}) VALUES ({values})"
                cur.execute(query, tuple(row))
            conn.commit()
            logging.info("Data loaded successfully.")
            return True
        except Exception as e:
            conn.rollback()  # Rollback changes in case of error
            logging.error(f"Error inserting data into Snowflake: {e}")
            raise  # Re-raise the exception to be handled by the calling function

    except FileNotFoundError:
        logging.error(f"CSV file not found: {file_location}")
        return False
    except snowflake.connector.errors.ProgrammingError as e:
        logging.error(f"Snowflake connection or query error: {e}")
        return False
    except pd.errors.EmptyDataError:
        logging.error(f"CSV file is empty: {file_location}")
        return False
    except pd.errors.ParserError:
        logging.error(f"Error parsing CSV file: {file_location}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logging.info("Snowflake connection closed.")

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
