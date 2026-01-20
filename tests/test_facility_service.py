import pytest
import uuid
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import invalidTenantId


# --- Test functions ---

@pytest.mark.positive
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


@pytest.mark.positive
def test_search_facility():
    """Test to search for a facility by ID. Creates facility if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    facilityId = extract_id_from_file("Facility ID:")
    if not facilityId:
        # Create facility internally if ID not found
        print("Facility ID not found in file, creating new facility...")
        res = create_facility(token, client)
        assert res.status_code in [200, 202], f"Facility creation failed: {res.text}"
        facilityId = res.json()["Facility"]["id"]
        print(f"Facility created with ID: {facilityId}")

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


@pytest.mark.negative
def test_create_facility_with_invalid_tenant_id():
    """Negative test: Creating facility with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_facility(token, client, tenant_id=invalidTenantId)
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating facility with invalid tenantId returned 401")


@pytest.mark.negative
def test_search_facility_with_invalid_tenant_id():
    """Negative test: Searching facility with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    facility_id = extract_id_from_file("Facility ID:")
    if not facility_id:
        # Create a new facility if ID not found
        res = create_facility(token, client)
        assert res.status_code in [200, 202], f"Facility creation failed: {res.text}"
        facility_id = res.json()["Facility"]["id"]

    payload = load_payload("facility", "search_facility.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Facility"]["id"] = [facility_id]

    url = f"/facility/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


# --- Reusable Functions ---

def create_facility(token, client, tenant_id=None):
    """
    Create a facility.

    Args:
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
    """
    payload = load_payload("facility", "create_facility.json")
    payload["RequestInfo"] = get_request_info(token)
    # Inject dynamic values
    payload["Facility"]["clientReferenceId"] = str(uuid.uuid4())

    # Override tenantId if provided (for negative testing)
    if tenant_id is not None:
        payload["Facility"]["tenantId"] = tenant_id

    return client.post("/facility/v1/_create", payload)


