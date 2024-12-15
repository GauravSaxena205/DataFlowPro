import requests
import json



def load_api_data(config, endpoint_name, params=None):
    """
    Loads data from a specified API endpoint.

    Args:
        config (dict): A dictionary containing API configuration details. 
                       Must include 'api_base_url' and 'endpoints'.
        endpoint_name (str): The name of the endpoint to access 
                             (e.g., 'posts', 'comments').
        params (dict, optional): A dictionary of parameters to send with 
                                 the request (e.g., for filtering). 
                                 Defaults to None.

    Returns:
        dict or str: A dictionary containing the API response data if 
                     successful, otherwise an error message string.
    """
    try:
        # Validate configuration
        if not isinstance(config, dict) or 'api_base_url' not in config or 'endpoints' not in config:
            return "Error: Invalid API configuration."

        # Check if endpoint exists
        if endpoint_name not in config['endpoints']:
            return f"Error: Endpoint '{endpoint_name}' not found in configuration."

        # Construct full URL
        url = config['api_base_url'] + config['endpoints'][endpoint_name]
        
        # Make API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Parse and return JSON response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        return f"Error: An error occurred during the API request: {e}"
    except json.JSONDecodeError as e:
        return f"Error: Could not decode JSON response: {e}"


def main():
    # Example API configuration
    api_config = {
        'api_base_url': 'https://jsonplaceholder.typicode.com',
        'endpoints': {
            'posts': '/posts',
            'comments': '/comments',
            'albums': '/albums',
            'photos': '/photos',
            'todos': '/todos',
            'users': '/users'
        }
    }

    # Test various API data loading scenarios
    posts = load_api_data(api_config, 'posts')
    
    #print(f"Posts: {posts}")  # Prints the JSON response, or an error message
    return posts,"JSONPLACEHOLDER_RZ","BRONZE","LZ"
    
    '''
    comments = load_api_data(api_config, 'comments', params={'postId': 1})
    print(f"Comments for post 1: {comments}")

    invalid_endpoint = load_api_data(api_config, 'invalid_endpoint')
    print(f"Invalid endpoint result: {invalid_endpoint}")

    bad_config = load_api_data({}, 'posts')
    print(f"Bad config result: {bad_config}")
    '''

if __name__ == "__main__":
    main()