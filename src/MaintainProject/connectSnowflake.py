
import json
import snowflake.connector
import pandas as pd
import datetime
SNOWFLAKE_CONFIG_PATH='C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\configs\\snowflakeConnConfig.json'

data_frame,table_name,database, schema = None, None, None, None


def connect_snowflake(sf_config): 
    with open(sf_config, 'r') as f:
        sf_config = json.load(f)

    conn = snowflake.connector.connect( 
        user=sf_config['username'], 
        password=sf_config['password'], 
        account=sf_config['account_identifier'], 
        warehouse=sf_config['warehouse'], 
        database=sf_config['database'], 
        schema=sf_config['schema']) 
    return conn 

def upload_to_snowflake(conn, data_frame, table_name, db, schema): 
    cursor = conn.cursor() 
    cursor.execute(f"USE DATABASE {db}") 
    cursor.execute(f"USE SCHEMA {schema}") 
    
    df_sf = pd.DataFrame(data_frame)
   
    df_sf.to_sql(table_name, conn, if_exists='append', index=False, method='multi') 
    cursor.close() 

def main(data_frame,table_name, db, schema):
    conn = connect_snowflake(SNOWFLAKE_CONFIG_PATH)
    upload_to_snowflake(conn,data_frame,table_name, db, schema)
    
    

if __name__ == "__main__": main(data_frame,table_name, database, schema)