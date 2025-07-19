from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId, search_params, boundaryCode
import uuid
import json

def test_create_household():
    token = get_auth_token("user")  # Or the relevant service role
    client = APIClient("user")  # Injects token automatically

    # Load payload and manually insert dynamic RequestInfo
    payload = load_payload("household", "create_household.json")

    # Generate dynamic IDs
    payload["Household"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Household"]["address"]["clientReferenceId"] = str(uuid.uuid4())  
    payload["Household"]["address"]["locality"]["code"]=boundaryCode

    # Inject RequestInfo manually
    payload["RequestInfo"] = get_request_info(token)

    res = client.post("/household/v1/_create", payload)
    assert res.status_code in [200, 202], f"Unexpected response: {res.text}"

    response_data = res.json()
    householdId = response_data["Household"]["id"]
    householdClientReferenceId = response_data["Household"]["clientReferenceId"]
    householdAddressObject = response_data["Household"]["address"]

    with open("output/data.txt", "w") as f:
        f.write("\n--- Household details ---\n")
        f.write(f"Household ID: {householdId}\n")
        f.write(f"Client Reference ID: {householdClientReferenceId}\n")
        f.write(f"Household Address: {householdAddressObject}\n")

    # Save full response
    with open("output/response.json", "w") as f:
        json.dump(res.json(), f, indent=2)


def test_search_household_by_id():
    token = get_auth_token("user")
    client = APIClient("user")

    # Extract Household ID from file
    with open("output/data.txt", "r") as f:
        lines = f.readlines()

    householdId = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("Household ID:")), None)
    assert householdId, "Household ID not found in file"

    print("Extracted Household ID:", householdId)

    # Load payload and inject dynamic data
    payload = load_payload("household", "search_household.json")
    payload["Household"]["id"] = [householdId]
    payload["RequestInfo"] = get_request_info(token)

    # Build query string from params
    query_string = "&".join(f"{k}={v}" for k, v in search_params.items())
    url = f"/household/v1/_search?{query_string}"

    res = client.post(url, payload)

    # Save response
    with open("output/response.json", "w") as f:
        json.dump(res.json(), f, indent=2)

    assert res.status_code == 200, f"Search failed: {res.text}"
    household_data = res.json().get("Households", [])
    assert householdId in [h["id"] for h in household_data], "Household not found"


