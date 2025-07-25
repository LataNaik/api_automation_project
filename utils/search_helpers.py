from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import search_params

def search_entity(entity_type, token, client, entity_id, payload_file, endpoint, response_key):
    payload = load_payload(entity_type, payload_file)
    
    # Dynamically pick the top-level key in payload (e.g. "Product", "ProductVariant")
    top_key = next(iter(payload))
    payload[top_key]["id"] = [entity_id]
    payload["RequestInfo"] = get_request_info(token)

    query_string = "&".join(f"{k}={v}" for k, v in search_params.items())
    url = f"{endpoint}?{query_string}"

    res = client.post(url, payload)
    assert res.status_code == 200, f"Search failed: {res.text}"

    response_data = res.json()
    return response_data.get(response_key, [])



def extract_id_from_file(label):
    with open("output/ids.txt", "r") as f:
        lines = f.readlines()
    return next((line.split(":", 1)[1].strip() for line in lines if line.startswith(label)), None)
