import requests
import json

def load_data_from_api(config):
    """
    Loads data from an API and optionally loads it into Snowflake.

    Args:
        config (dict): A dictionary containing API and Snowflake configuration.
                       Requires 'api_base_url', 'headers', and 'timeout'.
                       'snowflake_db', 'snowflake_schema', and 'snowflake_table' are optional for Snowflake loading.

    Returns:
        tuple: A tuple containing:
            - The JSON response data (or None if an error occurred).
            - An error message (or None if successful).
    """
    api_base_url = config.get('api_base_url')
    headers = config.get('headers', {})
    timeout = config.get('timeout', 30)
    snowflake_db = config.get('snowflake_db')
    snowflake_schema = config.get('snowflake_schema')
    snowflake_table = config.get('snowflake_table')

    if not api_base_url:
        return None, "Error: 'api_base_url' is missing from the configuration."

    try:
        response = requests.get(api_base_url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Optional Snowflake loading (replace with your actual Snowflake connection and loading logic)
        if snowflake_db and snowflake_schema and snowflake_table:
            try:
                # Placeholder for Snowflake loading - Replace this with your Snowflake connection and data loading code.
                print(f"Data would be loaded into Snowflake: {snowflake_db}.{snowflake_schema}.{snowflake_table}")
                # Example using a hypothetical snowflake_load function:
                # snowflake_load(data, snowflake_db, snowflake_schema, snowflake_table)

            except Exception as e:
                return data, f"Error loading data into Snowflake: {e}"

        return data, None

    except requests.exceptions.RequestException as e:
        return None, f"Error during API request: {e}"
    except json.JSONDecodeError as e:
        return None, f"Error decoding JSON response: {e}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

# Example usage:
config = {
    'api_base_url': 'https://jsonplaceholder.typicode.com/todos/1',  # Example API
    'headers': {'Content-Type': 'application/json'},
    'timeout': 30,
    'snowflake_db': 'my_database',  # Optional Snowflake config
    'snowflake_schema': 'my_schema',
    'snowflake_table': 'my_table'
}

data, error = load_data_from_api(config)

if error:
    print(f"Error: {error}")
else:
    print(f"Data loaded successfully: {data}")
