import pytest
from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from test_individual_service import create_individual
from utils.config import boundaryCode, invalidTenantId
import uuid
import json
import random

# Load the values from JSON file
with open("data/inputs.json", "r") as f:
    structure_data = json.load(f)


# --- Test functions ---

@pytest.mark.positive
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


@pytest.mark.positive
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


@pytest.mark.positive
def test_search_household():
    """Test to search for a household by ID. Creates household if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    householdId = extract_id_from_file("Household ID:")
    if not householdId:
        # Create household internally if ID not found
        print("Household ID not found in file, creating new household...")
        householdId, _, status_code = create_household(token, client)
        assert status_code in [200, 202], f"Household creation failed with status: {status_code}"
        print(f"Household created with ID: {householdId}")

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


@pytest.mark.positive
def test_search_householdMember_by_id():
    """Test to search for a household member by ID. Creates household member if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    memberId = extract_id_from_file("Household Member ID:")
    if not memberId:
        # Create household member internally if ID not found
        print("Household Member ID not found in file, creating new household member...")
        res = create_household_member(token, client)
        assert res.status_code in [200, 202], f"Household Member creation failed: {res.text}"
        memberId = res.json()["HouseholdMember"]["id"]
        print(f"Household Member created with ID: {memberId}")

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


@pytest.mark.negative
def test_create_householdMember_without_householdId():
    """Negative test: Creating household member without householdId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Use helper with householdId=None to test negative scenario
    res = create_household_member(token, client, household_id=None, household_client_ref_id=None)

    # Should fail with 400 Bad Request
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating member without householdId returned 400")


@pytest.mark.negative
def test_create_householdMember_without_individualId():
    """Negative test: Creating household member without individualId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Use helper with individualId=None to test negative scenario
    res = create_household_member(token, client, individual_id=None, individual_client_ref_id=None)

    # Should fail with 400 Bad Request
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating member without individualId returned 400")


@pytest.mark.negative
def test_create_household_with_invalid_tenant_id():
    """Negative test: Creating household with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_household(token, client, tenant_id=invalidTenantId)

    # Should fail with 401 Unauthorized
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating household with invalid tenantId returned 401")


@pytest.mark.negative
def test_create_householdMember_with_invalid_tenant_id():
    """Negative test: Creating household member with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_household_member(token, client, tenant_id=invalidTenantId)

    # Should fail with 401 Unauthorized
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating household member with invalid tenantId returned 401")


@pytest.mark.negative
def test_search_household_with_invalid_tenant_id():
    """Negative test: Searching household with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    household_id = extract_id_from_file("Household ID:")
    if not household_id:
        # Create a new household if ID not found
        household_id, _, status_code = create_household(token, client)
        assert status_code in [200, 202], f"Household creation failed with status: {status_code}"

    payload = load_payload("household", "search_household.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Household"]["id"] = [household_id]

    url = f"/household/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_householdMember_with_invalid_tenant_id():
    """Negative test: Searching household member with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    member_id = extract_id_from_file("Household Member ID:")
    if not member_id:
        # Create a new household member if ID not found
        res = create_household_member(token, client)
        assert res.status_code in [200, 202], f"Household Member creation failed: {res.text}"
        member_id = res.json()["HouseholdMember"]["id"]

    payload = load_payload("household", "search_householdMember.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HouseholdMember"]["id"] = [member_id]

    url = f"/household/member/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.positive
def test_update_household():
    """Test to update a household. Creates household internally first, then updates memberCount."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create household internally
    print("Creating household for update test...")
    householdId, householdClientReferenceId, status_code = create_household(token, client)
    assert status_code in [200, 202], f"Household creation failed with status: {status_code}"
    print(f"Household created with ID: {householdId}")

    # Step 2: Search for the household to get full data for update
    households = search_entity(
        entity_type="household",
        token=token,
        client=client,
        entity_id=householdId,
        payload_file="search_household.json",
        endpoint="/household/v1/_search",
        response_key="Households"
    )
    assert len(households) > 0, "Could not find created household"
    household_data = households[0]

    # Step 3: Update the household (change memberCount)
    original_member_count = household_data.get("memberCount", 1)
    new_member_count = original_member_count + 3
    response = update_household(token, client, household_data, new_member_count)
    assert response.status_code in [200, 202], f"Household update failed: {response.text}"

    # Step 4: Verify update
    updated_household = response.json()["Household"]
    assert updated_household["memberCount"] == new_member_count, f"memberCount not updated. Expected {new_member_count}, got {updated_household['memberCount']}"
    print(f"Household updated successfully. memberCount changed from {original_member_count} to {new_member_count}")


@pytest.mark.positive
def test_update_household_member():
    """Test to update a household member twice. Creates household, individual, and member internally first, then updates isHeadOfHousehold twice ending with true."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create household member (which internally creates household and individual)
    print("Creating household member for update test...")
    res = create_household_member(token, client)
    assert res.status_code in [200, 202], f"Household Member creation failed: {res.text}"
    member_data = res.json()["HouseholdMember"]
    member_id = member_data["id"]
    print(f"Household Member created with ID: {member_id}")

    # Step 2: Search for the member to get full data for update
    members = search_entity(
        entity_type="household",
        token=token,
        client=client,
        entity_id=member_id,
        payload_file="search_householdMember.json",
        endpoint="/household/member/v1/_search",
        response_key="HouseholdMembers"
    )
    assert len(members) > 0, "Could not find created household member"
    member_full_data = members[0]
    original_is_head = member_full_data.get("isHeadOfHousehold", False)
    print(f"Original isHeadOfHousehold: {original_is_head}")

    # Step 3: First update - set isHeadOfHousehold to False
    print("First update: Setting isHeadOfHousehold to False...")
    response1 = update_household_member(token, client, member_full_data, False)
    assert response1.status_code in [200, 202], f"First update failed: {response1.text}"
    updated_member1 = response1.json()["HouseholdMember"]
    assert updated_member1["isHeadOfHousehold"] == False, f"First update failed. Expected False, got {updated_member1['isHeadOfHousehold']}"
    print(f"First update successful. isHeadOfHousehold is now False")

    # Step 4: Second update - set isHeadOfHousehold to True
    print("Second update: Setting isHeadOfHousehold to True...")
    response2 = update_household_member(token, client, updated_member1, True)
    assert response2.status_code in [200, 202], f"Second update failed: {response2.text}"
    updated_member2 = response2.json()["HouseholdMember"]
    assert updated_member2["isHeadOfHousehold"] == True, f"Second update failed. Expected True, got {updated_member2['isHeadOfHousehold']}"
    print(f"Second update successful. isHeadOfHousehold is now True")

    print(f"Household Member updated successfully with 2 updates. Final isHeadOfHousehold: True")


# --- Helper function ---

def create_household(token, client, tenant_id=None):
    """
    Create a household.

    Args:
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
    """
    payload = load_payload("household", "create_household.json")

    # Inject dynamic values
    payload["Household"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Household"]["address"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Household"]["address"]["locality"]["code"] = boundaryCode
    selected_type = random.choice(structure_data["houseStructureTypes"])
    payload["Household"]["additionalFields"]["fields"][0]["value"] = selected_type
    payload["RequestInfo"] = get_request_info(token)

    # Override tenantId if provided (for negative testing)
    if tenant_id is not None:
        payload["Household"]["tenantId"] = tenant_id
        payload["Household"]["address"]["tenantId"] = tenant_id

    # Make the API call
    response = client.post("/household/v1/_create", payload)

    # For negative tests, return response directly
    if tenant_id is not None:
        return response

    # Handle error if status is not success
    if response.status_code not in [200, 202]:
        raise Exception(f"Household creation failed with status {response.status_code}: {response.text}")

    household_data = response.json()["Household"]
    household_id = household_data["id"]
    household_client_reference_id = household_data["clientReferenceId"]

    # Return all desired values including status_code
    return household_id, household_client_reference_id, response.status_code


def create_household_member(token, client, household_id="create", household_client_ref_id="create",
                            individual_id="create", individual_client_ref_id="create", tenant_id=None):
    """
    Create a household member.

    Args:
        household_id: Pass None to skip, "create" to create new, or provide existing ID
        household_client_ref_id: Pass None to skip, "create" to create new, or provide existing ID
        individual_id: Pass None to skip, "create" to create new, or provide existing ID
        individual_client_ref_id: Pass None to skip, "create" to create new, or provide existing ID
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
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

    # Override tenantId if provided (for negative testing)
    if tenant_id is not None:
        payload["HouseholdMember"]["tenantId"] = tenant_id

    res = client.post("/household/member/v1/_create", payload)
    return res


def update_household(token, client, household_data, new_member_count):
    """
    Update a household's memberCount.

    Args:
        household_data: Full household object from search
        new_member_count: New memberCount value to set
    """
    payload = load_payload("household", "update_household.json")

    # Copy required fields from the searched household
    payload["Household"]["id"] = household_data["id"]
    payload["Household"]["tenantId"] = household_data["tenantId"]
    payload["Household"]["clientReferenceId"] = household_data["clientReferenceId"]
    payload["Household"]["rowVersion"] = household_data["rowVersion"]
    payload["Household"]["auditDetails"] = household_data["auditDetails"]
    payload["Household"]["clientAuditDetails"] = household_data.get("clientAuditDetails")
    payload["Household"]["address"] = household_data["address"]
    payload["Household"]["memberCount"] = new_member_count
    payload["RequestInfo"] = get_request_info(token)

    response = client.post("/household/v1/_update", payload)
    return response


def update_household_member(token, client, member_data, new_is_head):
    """
    Update a household member's isHeadOfHousehold status.

    Args:
        member_data: Full household member object from search
        new_is_head: New isHeadOfHousehold value to set
    """
    payload = load_payload("household", "update_householdMember.json")

    # Copy required fields from the searched member
    payload["HouseholdMember"]["id"] = member_data["id"]
    payload["HouseholdMember"]["tenantId"] = member_data["tenantId"]
    payload["HouseholdMember"]["clientReferenceId"] = member_data["clientReferenceId"]
    payload["HouseholdMember"]["rowVersion"] = member_data["rowVersion"]
    payload["HouseholdMember"]["auditDetails"] = member_data["auditDetails"]
    payload["HouseholdMember"]["clientAuditDetails"] = member_data.get("clientAuditDetails")
    payload["HouseholdMember"]["householdId"] = member_data["householdId"]
    payload["HouseholdMember"]["householdClientReferenceId"] = member_data["householdClientReferenceId"]
    payload["HouseholdMember"]["individualId"] = member_data["individualId"]
    payload["HouseholdMember"]["individualClientReferenceId"] = member_data["individualClientReferenceId"]
    payload["HouseholdMember"]["isHeadOfHousehold"] = new_is_head
    payload["RequestInfo"] = get_request_info(token)

    response = client.post("/household/member/v1/_update", payload)
    return response