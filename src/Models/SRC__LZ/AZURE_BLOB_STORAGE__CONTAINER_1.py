from azure.storage.blob import BlobServiceClient, BlobClient
import io
import pandas as pd


def load_data_from_azure_blob(config):
    """
    Loads data from Azure Blob Storage.

    Args:
        config (dict): A dictionary containing the Azure Blob Storage configuration.
                       Must include at least one of 'connectionString' or 
                       ('accountName', 'accountKey').
                       Other keys ('containerName', 'blobName') are required.

    Returns:
        bytes: The content of the blob as bytes. Returns None if an error occurs.
    """
    # Validate required configuration keys
    required_keys = ('containerName', 'blobName')
    if not all(key in config for key in required_keys):
        raise ValueError(f"Missing required keys in config: {required_keys}")

    try:
        # Establish connection to Azure Blob Storage
        if 'connectionString' in config and config['connectionString']:
            blob_service_client = BlobServiceClient.from_connection_string(
                config['connectionString']
            )
        elif (
            'accountName' in config 
            and config['accountName'] 
            and 'accountKey' in config 
            and config['accountKey']
        ):
            # Construct connection string manually
            connect_str = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={config['accountName']};"
                f"AccountKey={config['accountKey']};"
                "EndpointSuffix=core.windows.net"
            )
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        else:
            raise ValueError(
                "Must provide either 'connectionString' or "
                "('accountName', 'accountKey')"
            )

        # Get blob client and download blob contents
        blob_client = blob_service_client.get_blob_client(
            container=config['containerName'],
            blob=config['blobName']
        )

        # Download the blob contents
        blob_data = blob_client.download_blob().readall()
        return blob_data

    except Exception as e:
        print(f"Error loading data from Azure Blob Storage: {e}")
        return None


def main():
    # Example configuration
    config = {
        'accountName': 'your_account_name',  # Replace with your account name
        'accountKey': 'your_account_key',    # Replace with your account key
        'containerName': 'your_container_name',  # Replace with your container name
        'blobName': 'your_blob_name',        # Replace with your blob name
        'connectionString': '',  # Leave empty if using accountName/accountKey
        'snowflake_db': '',
        'snowflake_schema': '',
        'snowflake_table': ''
    }

    # Load data from Azure Blob Storage
    data = load_data_from_azure_blob(config)

    if data:
        print(f"Data loaded successfully. Length: {len(data)} bytes")
        
        # Optional: Process the data 
        try:
            # Example for CSV decoding
            df = pd.read_csv(io.StringIO(data.decode('utf-8')))
            print("DataFrame preview:")
            print(df.head())
        except Exception as e:
            print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()