import os
import sys

# Add the src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Models.SRC__LZ import API__JSONPLACEHOLDER
from src.MaintainProject import connectSnowflake as SF


def main():
    # Capture data from API
    dataObj,table_name, database, schema = API__JSONPLACEHOLDER.main()
    
    # Save Obj into SF
    SF.main(dataObj,table_name, database, schema)


if __name__ == "__main__":
    main()