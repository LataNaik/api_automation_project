from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import search_params, boundaryCode
import uuid
import json


def test_create_individual():
    token = get_auth_token("user")
    client = APIClient(token=token)  # Use the token once

    # Load payload and manually insert dynamic RequestInfo
    payload = load_payload("individual", "create_individual.json")

    # Generate dynamic IDs
    payload["Individual"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Individual"]["address"][0]["clientReferenceId"] = str(uuid.uuid4())  
    payload["Individual"]["address"][0]["locality"]["code"]=boundaryCode
    payload["Individual"]["identifiers"][0]["clientReferenceId"]=str(uuid.uuid4())
    payload["Individual"]["skills"][0]["clientReferenceId"]=str(uuid.uuid4())
    
    # Inject RequestInfo manually
    payload["RequestInfo"] = get_request_info(token)

    res = client.post("/individual/v1/_create", payload)
    assert res.status_code in [200, 202], f"Unexpected response: {res.text}"

    response_data = res.json()
    individualId = response_data["Individual"]["id"]
    individualClientReferenceId = response_data["Individual"]["clientReferenceId"]
    individualIndId = response_data["Individual"]["individualId"]
    print("Newly created Individual Id:", individualId)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Individual details ---\n")
        f.write(f"Individual ID: {individualId}\n")
        f.write(f"Individual Client Reference ID: {individualClientReferenceId}\n")
        f.write(f"Individual Ind ID: {individualIndId}\n")

    # Save full response
    with open("output/response.json", "w") as f:
        json.dump(res.json(), f, indent=2)


def test_search_individual_by_id():
    token = get_auth_token("user")
    client = APIClient(token=token)  # Use the token once

    # Extract Individual ID from file
    with open("output/ids.txt", "r") as f:
        lines = f.readlines()

    individualId = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("Individual ID:")), None)
    assert individualId, "Individual ID not found in file"

    print("Extracted Individual ID:", individualId)

    # Load payload and inject dynamic data
    payload = load_payload("individual", "search_individual.json")
    payload["Individual"]["id"] = [individualId]
    payload["RequestInfo"] = get_request_info(token)

    # Build query string from params
    query_string = "&".join(f"{k}={v}" for k, v in search_params.items())
    url = f"/individual/v1/_search?{query_string}"

    res = client.post(url, payload)

    # Save response
    with open("output/response.json", "w") as f:
        json.dump(res.json(), f, indent=2)

    assert res.status_code == 200, f"Search failed: {res.text}"
    individual_data = res.json().get("Individual", [])
    assert individualId in [h["id"] for h in individual_data], "Individual not found"


