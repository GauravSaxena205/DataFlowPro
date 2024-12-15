import pandas as pd
import snowflake.connector
from snowflake.connector.errors import ProgrammingError

def load_csv_to_snowflake(config):
    """
    Loads data from a CSV file into a Snowflake table.

    Args:
        config (dict): A dictionary containing the following keys:
            - file_location (str): The path to the CSV file.
            - snowflake_db (str): The Snowflake database name.
            - snowflake_schema (str): The Snowflake schema name.
            - snowflake_table (str): The Snowflake table name.
            - snowflake_account (str): Your Snowflake account identifier.
            - snowflake_user (str): Your Snowflake username.
            - snowflake_password (str): Your Snowflake password.
            - snowflake_warehouse (str, optional): The Snowflake warehouse to use. Defaults to 'COMPUTE_WH'.

    Returns:
        bool: True if the data was successfully loaded, False otherwise. Prints error messages if loading fails.

    Raises:
        ValueError: If any required configuration parameters are missing.
        Exception: For other errors during the process.
    """

    required_keys = ['file_location', 'snowflake_db', 'snowflake_schema', 'snowflake_table', 'snowflake_account', 'snowflake_user', 'snowflake_password']
    if not all(key in config for key in required_keys):
        raise ValueError("Missing required keys in config. Requires: file_location, snowflake_db, snowflake_schema, snowflake_table, snowflake_account, snowflake_user, snowflake_password")

    file_location = config['file_location']
    snowflake_db = config['snowflake_db']
    snowflake_schema = config['snowflake_schema']
    snowflake_table = config['snowflake_table']
    snowflake_account = config['snowflake_account']
    snowflake_user = config['snowflake_user']
    snowflake_password = config['snowflake_password']
    snowflake_warehouse = config.get('snowflake_warehouse', 'COMPUTE_WH')  # use COMPUTE_WH as default

    try:
        # Load CSV into pandas DataFrame
        df = pd.read_csv(file_location)

        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=snowflake_account,
            user=snowflake_user,
            password=snowflake_password,
            database=snowflake_db,
            schema=snowflake_schema,
            warehouse=snowflake_warehouse
        )

        cur = conn.cursor()

        # Get column names from DataFrame
        columns = ','.join(df.columns)

        # Prepare the insert statement (using parameterized queries for security)
        insert_statement = f"INSERT INTO {snowflake_db}.{snowflake_schema}.{snowflake_table} ({columns}) VALUES (%s)"

        # Insert data row by row (more efficient for large datasets than using pandas.to_sql)
        for index, row in df.iterrows():
            values = tuple(row)  # Convert row to tuple
            try:
                cur.execute(insert_statement, values)
            except ProgrammingError as e:
                print(f"Error inserting row {index + 1}: {e}")  # report the error and continue with the next row
                continue  # Skip the row that caused an error

        conn.commit()
        print("Data loaded successfully.")
        return True

    except FileNotFoundError:
        print(f"Error: CSV file not found at {file_location}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# Example configuration
config = {
    'file_location': '/path/to/your/file.csv',  # Replace with your file path
    'snowflake_db': 'your_database',            # Replace with your database
    'snowflake_schema': 'your_schema',          # Replace with your schema
    'snowflake_table': 'your_table',            # Replace with your table name
    'snowflake_account': 'your_account_identifier',  # Replace with your account identifier (e.g., your_account.snowflakecomputing.com)
    'snowflake_user': 'your_username',          # Replace with your username
    'snowflake_password': 'your_password'       # Replace with your password
}

success = load_csv_to_snowflake(config)
print(f"Load successful: {success}")
