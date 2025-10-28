from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import boundaryCode, individual
import uuid
import json


# --- Test functions ---

def test_create_individual():
    token = get_auth_token("user")
    client = APIClient(token=token)

    individualId, individualClientReferenceId, individualIndId, status_code  = create_individual(token, client)
    
    # Assertion in test
    assert status_code in [200, 202], f"Individual creation failed: {status_code}"

    print("Individual created with ID:", individualId)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Individual details ---\n")
        f.write(f"Individual ID: {individualId}\n")
        f.write(f"Individual Client Reference ID: {individualClientReferenceId}\n")
        f.write(f"Individual Ind ID: {individualIndId}\n")


def test_search_individual():
    token = get_auth_token("user")
    client = APIClient(token=token)

    individualId = extract_id_from_file("Individual ID:")
    assert individualId, "Individual ID not found in file"

    individuals = search_entity(
        entity_type="individual",
        token=token,
        client=client,
        entity_id=individualId,
        payload_file="search_individual.json",
        endpoint=f"/{individual}/v1/_search",
        response_key="Individual"
    )

    assert individualId in [i["id"] for i in individuals], "Individual not found"
    print("Individual found with ID:", individualId)


# --- Helper function (no assertion) ---
def create_individual(token, client):
    payload = load_payload("individual", "create_individual.json")

    # Inject dynamic values
    payload["Individual"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Individual"]["address"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["Individual"]["address"][0]["locality"]["code"] = boundaryCode
    payload["Individual"]["identifiers"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["Individual"]["skills"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["RequestInfo"] = get_request_info(token)
    
    url = f"/{individual}/v1/_create"
    response = client.post(url, payload)
    # Handle error if status is not success
    if response.status_code not in [200, 202]:
        raise Exception(f"Household creation failed with status {response.status_code}: {response.text}")

    individual_data = response.json()["Individual"]
    individual_id = individual_data["id"]
    individual_client_reference_id = individual_data["clientReferenceId"]
    individual_ind_id = individual_data["individualId"]

    # Return all desired values including status_code
    return individual_id, individual_client_reference_id, individual_ind_id, response.status_code

