from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId
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

    # Inject RequestInfo manually
    payload["RequestInfo"] = get_request_info(token)

    res = client.post("/household/v1/_create", payload)
    assert res.status_code in [200, 202], f"Unexpected response: {res.text}"

    response_data = res.json()
    householdId = response_data["Household"]["id"]
    householdClientReferenceId = response_data["Household"]["clientReferenceId"]
    householdAddressObject = response_data["Household"]["address"]

    with open("output/data.txt", "w") as f:
        f.write(f"Household ID: {householdId}\n")
        f.write(f"Client Reference ID: {householdClientReferenceId}\n")
        f.write(f"Household Address: {householdAddressObject}\n")

    # Save full response
    with open("output/response.json", "w") as f:
        json.dump(res.json(), f, indent=2)


def test_search_household_by_id():
    token = get_auth_token("user")  # Or the relevant service role
    client = APIClient("user")  # Injects token automatically
    # Read the text file and extract Household ID
    with open("output/data.txt", "r") as f:
        lines = f.readlines()

    # Initialize variable
    householdId = None

    # Loop through lines and extract the ID from the label
    for line in lines:
        if line.startswith("Household ID:"):
            householdId = line.split("Household ID:")[1].strip()

    # Use householdId in your next request
    # print("Extracted Household ID:", householdId)

     # Load payload and manually insert dynamic RequestInfo
    payload = load_payload("household", "search_household.json")
    
     # Generate dynamic IDs
    payload["Household"]["id"] = [householdId] 

    # Query parameters
    # params = {
    #     "limit": 200,
    #     "offset": 0,
    #     "tenantId": "mz"
    # }

    # Inject RequestInfo manually
    payload["RequestInfo"] = get_request_info(token)

    res = client.post("/household/v1/_search?limit=200&offset=0&tenantId=mz", payload)
            # Save full response
    with open("output/response.json", "w") as f:
        json.dump(res.json(), f, indent=2)
    assert res.status_code == 200
    household_data = res.json().get("Households", [])
    # assert any(h["id"] == householdId for h in household_data), "Household not found"
    assert householdId.strip() in [h["id"].strip() for h in household_data], "Household not found"
