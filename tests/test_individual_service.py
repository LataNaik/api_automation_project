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

