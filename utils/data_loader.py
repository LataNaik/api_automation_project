import json
import os

def load_payload(service_name, filename):
    """
    Load a JSON payload file from the payloads/<service_name>/ directory.
    
    Args:
        service_name (str): The name of the microservice folder (e.g., 'household')
        filename (str): The JSON file name (e.g., 'create_household.json')
    
    Returns:
        dict: The loaded JSON as a Python dictionary.
    """
    base_path = os.path.dirname(__file__)  # current directory: utils/
    file_path = os.path.join(base_path, "..", "payloads", service_name, filename)

    with open(os.path.abspath(file_path), 'r', encoding='utf-8') as f:
        return json.load(f)
