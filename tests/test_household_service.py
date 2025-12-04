from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from test_individual_service import create_individual
from utils.config import boundaryCode
import uuid
import json
import random

# Load the values from JSON file
with open("data/inputs.json", "r") as f:
    structure_data = json.load(f)


# --- Test functions ---

def test_create_household():
    token = get_auth_token("user")
    client = APIClient(token=token)

    householdId, householdClientReferenceId, status_code = create_household(token, client)
    assert status_code in [200, 202], f"Household creation failed with status: {status_code}"

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Household details ---\n")
        f.write(f"Household ID: {householdId}\n")
        f.write(f"Household Client Reference ID: {householdClientReferenceId}\n")

    print("Household created with ID:", householdId)

  
def test_create_householdMember():
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_household_member(token, client)
    assert res.status_code in [200, 202], f"Unexpected response: {res.text}"

    response_data = res.json()
    memberId = response_data["HouseholdMember"]["id"]
    clientRefId = response_data["HouseholdMember"]["clientReferenceId"]
    assert memberId, "Household Member ID missing in response"

    print("Created Household Member ID:", memberId)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Member details ---\n")
        f.write(f"Household Member ID: {memberId}\n")
        f.write(f"Household Member Client Reference ID: {clientRefId}\n")


def test_search_household():
    token = get_auth_token("user")
    client = APIClient(token=token)

    householdId = extract_id_from_file("Household ID:")
    assert householdId, "Household ID not found in file"

    households = search_entity(
        entity_type="household",
        token=token,
        client=client,
        entity_id=householdId,
        payload_file="search_household.json",
        endpoint="/household/v1/_search",
        response_key="Households"
    )

    assert householdId in [h["id"] for h in households], "Household not found"
    print("Household found with ID:", householdId)


def test_search_householdMember_by_id():
    token = get_auth_token("user")
    client = APIClient(token=token)  # Use the token once

    memberId = extract_id_from_file("Household Member ID:")
    assert memberId, "Household Member not found in file"

    members = search_entity(
        entity_type="household",
        token=token,
        client=client,
        entity_id=memberId,
        payload_file="search_householdMember.json",
        endpoint="/household/member/v1/_search",
        response_key="HouseholdMembers"
    )

    assert memberId in [v["id"] for v in members], "Household Member not found"
    print("Household Member found with ID:", memberId)


def test_create_householdMember_without_householdId():
    """Negative test: Creating household member without householdId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Use helper with householdId=None to test negative scenario
    res = create_household_member(token, client, household_id=None, household_client_ref_id=None)

    # Should fail with 400 Bad Request
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating member without householdId returned 400")


def test_create_householdMember_without_individualId():
    """Negative test: Creating household member without individualId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Use helper with individualId=None to test negative scenario
    res = create_household_member(token, client, individual_id=None, individual_client_ref_id=None)

    # Should fail with 400 Bad Request
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating member without individualId returned 400")


# --- Helper function ---

def create_household(token, client):
    payload = load_payload("household", "create_household.json")

    # Inject dynamic values
    payload["Household"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Household"]["address"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Household"]["address"]["locality"]["code"] = boundaryCode
    selected_type = random.choice(structure_data["houseStructureTypes"])
    payload["Household"]["additionalFields"]["fields"][0]["value"] = selected_type
    payload["RequestInfo"] = get_request_info(token)

    # Make the API call
    response = client.post("/household/v1/_create", payload)

    # Handle error if status is not success
    if response.status_code not in [200, 202]:
        raise Exception(f"Household creation failed with status {response.status_code}: {response.text}")

    household_data = response.json()["Household"]
    household_id = household_data["id"]
    household_client_reference_id = household_data["clientReferenceId"]

    # Return all desired values including status_code
    return household_id, household_client_reference_id, response.status_code


def create_household_member(token, client, household_id="create", household_client_ref_id="create",
                            individual_id="create", individual_client_ref_id="create"):
    """
    Create a household member.

    Args:
        household_id: Pass None to skip, "create" to create new, or provide existing ID
        household_client_ref_id: Pass None to skip, "create" to create new, or provide existing ID
        individual_id: Pass None to skip, "create" to create new, or provide existing ID
        individual_client_ref_id: Pass None to skip, "create" to create new, or provide existing ID
    """
    # Create or use provided household
    if household_id == "create":
        householdId, householdClientReferenceId, _ = create_household(token, client)
    else:
        householdId = household_id
        householdClientReferenceId = household_client_ref_id

    # Create or use provided individual
    if individual_id == "create":
        individualId, individualClientReferenceId, _, _ = create_individual(token, client)
    else:
        individualId = individual_id
        individualClientReferenceId = individual_client_ref_id

    payload = load_payload("household", "create_householdMember.json")

    payload["HouseholdMember"]["clientReferenceId"] = str(uuid.uuid4())
    payload["HouseholdMember"]["householdId"] = householdId
    payload["HouseholdMember"]["householdClientReferenceId"] = householdClientReferenceId
    payload["HouseholdMember"]["individualId"] = individualId
    payload["HouseholdMember"]["individualClientReferenceId"] = individualClientReferenceId
    payload["RequestInfo"] = get_request_info(token)

    res = client.post("/household/member/v1/_create", payload)
    return res