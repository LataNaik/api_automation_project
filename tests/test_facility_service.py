import uuid
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file


# --- Test functions ---

def test_create_facility():
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_facility(token, client)
    assert res.status_code in [200, 202], f"Facility creation failed: {res.text}"

    facilityId = res.json()["Facility"]["id"]
    assert facilityId, "Facility ID not found in response"
    print("Facility created with ID:", facilityId)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Facility details ---\n")
        f.write(f"Facility ID: {facilityId}\n")


def test_search_facility():
    token = get_auth_token("user")
    client = APIClient(token=token)

    facilityId = extract_id_from_file("Facility ID:")
    assert facilityId, "Facility ID not found in file"

    facilitys = search_entity(
        entity_type="facility",
        token=token,
        client=client,
        entity_id=facilityId,
        payload_file="search_facility.json",
        endpoint="/facility/v1/_search",
        response_key="Facilities"
    )

    assert facilityId in [p["id"] for p in facilitys], "Facility not found"
    print("Facility found with ID:", facilityId)



# --- Reusable Functions ---

def create_facility(token, client):
    payload = load_payload("facility", "create_facility.json")
    payload["RequestInfo"] = get_request_info(token)
    # Inject dynamic values
    payload["Facility"]["clientReferenceId"] = str(uuid.uuid4())
    return client.post("/facility/v1/_create", payload)


