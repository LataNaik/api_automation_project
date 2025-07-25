from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from test_household_service import create_household
from test_individual_service import create_individual

import uuid
import json
import random


# --- Test functions ---    
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

    with open("output/response.json", "w") as f:
        json.dump(response_data, f, indent=2)


def test_search_householdMember_by_id():
    token = get_auth_token("user")
    client = APIClient(token=token)  # Use the token once

    memberId = extract_id_from_file("Household Member ID:")
    assert memberId, "Household Member not found in file"
    
    members = search_entity(
        entity_type="householdMember",
        token=token,
        client=client,
        entity_id=memberId,
        payload_file="search_householdMember.json",
        endpoint="/household/member/v1/_search",
        response_key="HouseholdMembers"
    )
    
    assert memberId in [v["id"] for v in members], "Household Member not found"
    print("Household Member found with ID:", memberId)


# --- Reusable Functions ---

def create_household_member(token, client):

    householdId, householdClientReferenceId, _ = create_household(token, client)
    individualId, individualClientReferenceId, _, _ = create_individual(token, client)
    payload = load_payload("householdMember", "create_householdMember.json")

    payload["HouseholdMember"]["clientReferenceId"] = str(uuid.uuid4())
    payload["HouseholdMember"]["householdId"] = householdId
    payload["HouseholdMember"]["householdClientReferenceId"] = householdClientReferenceId
    payload["HouseholdMember"]["individualId"] = individualId
    payload["HouseholdMember"]["individualClientReferenceId"] = individualClientReferenceId
    payload["RequestInfo"] = get_request_info(token)

    res = client.post("/household/member/v1/_create", payload)
    return res