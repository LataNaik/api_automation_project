import pytest
from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import boundaryCode, individual, invalidTenantId
import uuid


# --- Test functions ---

@pytest.mark.positive
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


@pytest.mark.positive
def test_search_individual():
    """Test to search for an individual by ID. Creates individual if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    individualId = extract_id_from_file("Individual ID:")
    if not individualId:
        # Create individual internally if ID not found
        print("Individual ID not found in file, creating new individual...")
        individualId, _, _, status_code = create_individual(token, client)
        assert status_code in [200, 202], f"Individual creation failed with status: {status_code}"
        print(f"Individual created with ID: {individualId}")

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


@pytest.mark.negative
def test_create_individual_with_invalid_tenant_id():
    """Negative test: Creating individual with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_individual(token, client, tenant_id=invalidTenantId)

    # Should fail with 401 Unauthorized
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating individual with invalid tenantId returned 401")


@pytest.mark.negative
def test_search_individual_with_invalid_tenant_id():
    """Negative test: Searching individual with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    individual_id = extract_id_from_file("Individual ID:")
    if not individual_id:
        # Create a new individual if ID not found
        individual_id, _, _, status_code = create_individual(token, client)
        assert status_code in [200, 202], f"Individual creation failed with status: {status_code}"

    payload = load_payload("individual", "search_individual.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Individual"]["id"] = [individual_id]

    url = f"/{individual}/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.positive
def test_update_individual():
    """Test to update an individual. Creates individual internally first, then updates the name."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create individual internally
    print("Creating individual for update test...")
    individualId, individualClientReferenceId, individualIndId, status_code = create_individual(token, client)
    assert status_code in [200, 202], f"Individual creation failed with status: {status_code}"
    print(f"Individual created with ID: {individualId}")

    # Step 2: Search for the individual to get full data for update
    individuals = search_entity(
        entity_type="individual",
        token=token,
        client=client,
        entity_id=individualId,
        payload_file="search_individual.json",
        endpoint=f"/{individual}/v1/_search",
        response_key="Individual"
    )
    assert len(individuals) > 0, "Could not find created individual"
    individual_data = individuals[0]

    # Step 3: Update the individual (change givenName)
    original_name = individual_data["name"]["givenName"]
    new_given_name = f"Updated-{original_name}"
    response = update_individual(token, client, individual_data, new_given_name)
    assert response.status_code in [200, 202], f"Individual update failed: {response.text}"

    # Step 4: Verify update
    updated_individual = response.json()["Individual"]
    assert updated_individual["name"]["givenName"] == new_given_name, f"givenName not updated. Expected {new_given_name}, got {updated_individual['name']['givenName']}"
    print(f"Individual updated successfully. givenName changed from '{original_name}' to '{new_given_name}'")


@pytest.mark.positive
def test_delete_individual():
    """Test to delete an individual. Creates individual internally first, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create individual internally
    print("Creating individual for delete test...")
    individual_data, individual_status = create_individual_full(token, client)
    assert individual_status in [200, 202], f"Individual creation failed with status: {individual_status}"
    individual_id = individual_data['id']
    print(f"Individual created with ID: {individual_id}")

    # Step 2: Delete the individual
    print("Deleting individual...")
    response = delete_individual(token, client, individual_data)
    assert response.status_code in [200, 202], f"Individual delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_individual = response.json()["Individual"]
    assert deleted_individual["isDeleted"] == True, f"Individual not marked as deleted"
    print(f"Individual {individual_id} deleted successfully")


# --- Helper function (no assertion) ---
def create_individual(token, client, tenant_id=None):
    """
    Create an individual.

    Args:
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
    """
    payload = load_payload("individual", "create_individual.json")

    # Inject dynamic values
    payload["Individual"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Individual"]["address"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["Individual"]["address"][0]["locality"]["code"] = boundaryCode
    payload["Individual"]["identifiers"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["Individual"]["skills"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["RequestInfo"] = get_request_info(token)

    # Override tenantId if provided (for negative testing)
    if tenant_id is not None:
        payload["Individual"]["tenantId"] = tenant_id
        payload["Individual"]["address"][0]["tenantId"] = tenant_id

    url = f"/{individual}/v1/_create"
    response = client.post(url, payload)

    # For negative tests, return response directly
    if tenant_id is not None:
        return response

    # Handle error if status is not success
    if response.status_code not in [200, 202]:
        raise Exception(f"Individual creation failed with status {response.status_code}: {response.text}")

    individual_data = response.json()["Individual"]
    individual_id = individual_data["id"]
    individual_client_reference_id = individual_data["clientReferenceId"]
    individual_ind_id = individual_data["individualId"]

    # Return all desired values including status_code
    return individual_id, individual_client_reference_id, individual_ind_id, response.status_code


def update_individual(token, client, individual_data, new_given_name):
    """
    Update an individual's givenName.

    Args:
        individual_data: Full individual object from search
        new_given_name: New givenName value to set
    """
    payload = load_payload("individual", "update_individual.json")

    # Copy required fields from the searched individual
    payload["Individual"]["id"] = individual_data["id"]
    payload["Individual"]["tenantId"] = individual_data["tenantId"]
    payload["Individual"]["clientReferenceId"] = individual_data["clientReferenceId"]
    payload["Individual"]["rowVersion"] = individual_data["rowVersion"]
    payload["Individual"]["individualId"] = individual_data["individualId"]
    payload["Individual"]["auditDetails"] = individual_data["auditDetails"]
    payload["Individual"]["clientAuditDetails"] = individual_data.get("clientAuditDetails")

    # Copy and update name
    payload["Individual"]["name"] = individual_data["name"].copy()
    payload["Individual"]["name"]["givenName"] = new_given_name

    # Copy other required fields
    payload["Individual"]["gender"] = individual_data.get("gender")
    payload["Individual"]["dateOfBirth"] = individual_data.get("dateOfBirth")
    payload["Individual"]["mobileNumber"] = individual_data.get("mobileNumber")
    payload["Individual"]["address"] = individual_data.get("address", [])
    payload["Individual"]["identifiers"] = individual_data.get("identifiers", [])
    payload["Individual"]["skills"] = individual_data.get("skills", [])

    payload["RequestInfo"] = get_request_info(token)

    url = f"/{individual}/v1/_update"
    response = client.post(url, payload)
    return response


def create_individual_full(token, client):
    """
    Create an individual and return full data for delete operations.

    Returns:
        Tuple of (individual_data, status_code)
    """
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

    if response.status_code not in [200, 202]:
        raise Exception(f"Individual creation failed with status {response.status_code}: {response.text}")

    return response.json()["Individual"], response.status_code


def delete_individual(token, client, individual_data):
    """
    Delete an individual (soft delete by setting isDeleted=true).

    Args:
        individual_data: Full individual object from create response
    """
    payload = load_payload("individual", "delete_individual.json")

    # Copy required fields from the created individual
    payload["Individual"]["id"] = individual_data["id"]
    payload["Individual"]["tenantId"] = individual_data["tenantId"]
    payload["Individual"]["clientReferenceId"] = individual_data["clientReferenceId"]
    payload["Individual"]["rowVersion"] = individual_data["rowVersion"]
    payload["Individual"]["auditDetails"] = individual_data["auditDetails"]
    payload["Individual"]["clientAuditDetails"] = individual_data.get("clientAuditDetails")
    payload["Individual"]["individualId"] = individual_data["individualId"]
    payload["Individual"]["name"] = individual_data["name"]
    payload["Individual"]["gender"] = individual_data.get("gender")
    payload["Individual"]["dateOfBirth"] = individual_data.get("dateOfBirth")
    payload["Individual"]["mobileNumber"] = individual_data.get("mobileNumber")
    payload["Individual"]["address"] = individual_data.get("address", [])
    payload["Individual"]["identifiers"] = individual_data.get("identifiers", [])
    payload["Individual"]["skills"] = individual_data.get("skills", [])
    payload["Individual"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{individual}/v1/_delete"
    response = client.post(url, payload)
    return response

