import os
from shareplum import Site, Office365
from shareplum.site import Version
import snowflake.connector
import pandas as pd

def load_sharepoint_data_to_snowflake(config):
    """
    Loads data from a SharePoint file to a Snowflake table.

    Args:
        config (dict): A dictionary containing the SharePoint and Snowflake connection details. See example below.

    Returns:
        bool: True if the data was successfully loaded, False otherwise. Prints error messages if failure occurs.
    """
    try:
        # SharePoint Connection
        site_url = f"https://{config['Config']['site_name']}.sharepoint.com/sites/{config['Config']['site_id']}"  # Adapt if needed
        authcookie = Office365(
            config['Config']['site_name'], username="", password=""
        ).GetCookies()  # Replace with your authentication method (e.g., using OAuth)
        site = Site(site_url, version=Version.v3, authcookie=authcookie)
        folder = site.Folder(config['Config']['folder_name'] or config['Config']['folder_id'])  # Use folder_name if folder_id is missing.
        file = folder.get_file(config['Config']['file_name'])

        # Download file content
        if file:
            with open(config['Config']['file_name'], 'wb') as f:
                f.write(file.read())

            # Read File, assuming its a CSV
            try:
                df = pd.read_csv(config['Config']['file_name'])
            except pd.errors.EmptyDataError:
                print("Error: SharePoint file is empty.")
                return False
            except pd.errors.ParserError:
                print("Error: Could not parse the SharePoint file. Check its format (CSV expected).")
                return False
            except FileNotFoundError:
                print("Error: File not found after download.")
                return False

            # Snowflake Connection
            conn = snowflake.connector.connect(
                account="",  # Replace with your Snowflake Account Identifier
                user="",  # Replace with your Snowflake User
                password="",  # Replace with your Snowflake Password
                database=config['Config']['snowflake_db'],
                schema=config['Config']['snowflake_schema'],
            )

            with conn.cursor() as cur:
                # Create table if it doesn't exist (add appropriate column definitions)
                create_table_sql = f"""
                    CREATE OR REPLACE TABLE {config['Config']['snowflake_table']} (
                        -- Add your column definitions here
                        col1 VARCHAR(255),
                        col2 NUMBER,
                        -- ...more columns...
                    );
                """
                cur.execute(create_table_sql)

                # Insert data (adjust based on your dataframe and table schema)
                for index, row in df.iterrows():
                    insert_sql = f"""
                        INSERT INTO {config['Config']['snowflake_table']} (col1, col2, ...)
                        VALUES ('{row['col1']}', {row['col2']}, ...);  -- Adapt to your column names and data types
                    """
                    cur.execute(insert_sql)
                conn.commit()

            os.remove(config['Config']['file_name'])  # remove the downloaded file

            return True

        else:
            print("Error: File not found in SharePoint.")
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage:
config = {
    'Config': {
        'site_name': 'your_sharepoint_site_name',
        'site_id': 'your_sharepoint_site_id',
        'folder_name': 'your_folder_name',  # Or folder_id
        'folder_id': '',  # Optional: Folder ID if you don't want to use the folder name.
        'file_name': 'your_file.csv',
        'snowflake_db': 'your_snowflake_db',
        'snowflake_schema': 'your_snowflake_schema',
        'snowflake_table': 'your_snowflake_table'
    }
}

success = load_sharepoint_data_to_snowflake(config)
if success:
    print("Data successfully loaded to Snowflake.")
else:
    print("Failed to load data to Snowflake.")
