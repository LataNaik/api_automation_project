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

def clear_ids_file():
    """
    Clear the ids.txt file to start fresh test execution.
    This function removes all content from output/ids.txt file.
    """
    base_path = os.path.dirname(__file__)  # current directory: utils/
    ids_file_path = os.path.join(base_path, "..", "output", "ids.txt")

    try:
        with open(os.path.abspath(ids_file_path), 'w', encoding='utf-8') as f:
            f.write("")
        print("✓ Cleared ids.txt file for fresh test execution")
    except Exception as e:
        print(f"Warning: Could not clear ids.txt file: {e}")
