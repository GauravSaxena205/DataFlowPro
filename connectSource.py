import json
import requests

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

def get_api_data(config, endpoint):
    url = config['api_base_url'] + config['endpoints'][endpoint]
    headers = config['headers']
    timeout = config['timeout']
    
    response = requests.get(url, headers=headers, timeout=timeout, verify =False)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def main():
    config = load_config('C:\\Users\\218433\\Documents\\DataFlowPro\\config\\sourceConfig.json')
    
    # Example: Fetch data from the 'posts' endpoint
    data = get_api_data(config, 'posts')
    print(data)

if __name__ == "__main__":
    main()