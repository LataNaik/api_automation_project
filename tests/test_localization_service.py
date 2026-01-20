import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import extract_id_from_file
from utils.config import tenantId, invalidTenantId


# --- Test functions ---

@pytest.mark.positive
def test_upsert_localization():
    token = get_auth_token("user")
    client = APIClient(token=token)

    message_code, status_code = upsert_localization(token, client)
    assert status_code in [200, 202], f"Localization upsert failed with status: {status_code}"

    print("Localization message upserted with code:", message_code)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Localization details ---\n")
        f.write(f"Localization Code: {message_code}\n")


@pytest.mark.positive
def test_search_localization():
    """Test to search for a localization message by code. Creates message if code not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    message_code = extract_id_from_file("Localization Code:")
    if not message_code:
        # Create localization message internally if code not found
        print("Localization Code not found in file, creating new localization message...")
        message_code, status_code = upsert_localization(token, client)
        assert status_code in [200, 202], f"Localization upsert failed with status: {status_code}"
        print(f"Localization message created with code: {message_code}")

    messages = search_localization(token, client, "hcm-test", "en_MZ")

    assert message_code in [m["code"] for m in messages], "Localization message not found"
    print("Localization message found with code:", message_code)


@pytest.mark.negative
def test_upsert_localization_with_invalid_tenant_id():
    """Negative test: Upserting localization with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    payload = load_payload("localization", "upsert_localization.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["tenantId"] = invalidTenantId

    url = "/localization/messages/v1/_upsert"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Upsert correctly rejected with status: {response.status_code}")


@pytest.mark.positive
def test_search_localization_with_invalid_tenant_id():
    """Test: Searching localization with any tenantId should succeed as localization is accessible for any tenant"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    payload = load_payload("localization", "search_localization.json")
    payload["RequestInfo"] = get_request_info(token)

    url = f"/localization/messages/v1/_search?tenantId={invalidTenantId}&locale=en_MZ&module=hcm-test"
    response = client.post(url, payload)

    assert response.status_code in [200, 202], f"Expected success status code, got: {response.status_code}"
    print(f"Search successful with status: {response.status_code}")


# --- Helper functions ---

def upsert_localization(token, client):
    payload = load_payload("localization", "upsert_localization.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["tenantId"] = tenantId

    url = "/localization/messages/v1/_upsert"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Localization upsert failed with status {response.status_code}: {response.text}")

    message_code = payload["messages"][0]["code"]
    return message_code, response.status_code


def search_localization(token, client, module, locale):
    payload = load_payload("localization", "search_localization.json")
    payload["RequestInfo"] = get_request_info(token)

    url = f"/localization/messages/v1/_search?tenantId={tenantId}&locale={locale}&module={module}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Localization search failed with status {response.status_code}: {response.text}")

    return response.json().get("messages", [])
