import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import extract_id_from_file
from utils.config import tenantId


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
    token = get_auth_token("user")
    client = APIClient(token=token)

    message_code = extract_id_from_file("Localization Code:")
    assert message_code, "Localization Code not found in file"

    messages = search_localization(token, client, "hcm-test", "en_MZ")

    assert message_code in [m["code"] for m in messages], "Localization message not found"
    print("Localization message found with code:", message_code)


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
