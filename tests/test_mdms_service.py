import pytest
import json
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import mdms


# --- Test functions ---

@pytest.mark.positive
def test_project_types():
    token = get_auth_token("user")
    client = APIClient(token=token)
    response = search_mdms_data(token, client, "HCM-PROJECT-TYPES.projectTypes")

    assert response.status_code == 200, f"MDMS Search failed: {response.text}"

    mdms_data = response.json().get("mdms", [])
    assert mdms_data, "No project types found in response"

    # Collect (outer id, inner code)
    project_types = [(item["data"]["id"], item["data"]["code"]) for item in mdms_data]

    # Assert both fields exist
    assert all(item[0] and item[1] for item in project_types), "Missing id or code in some project types"

    print("Project Types (id, code):")
    for pid, code in project_types:
        print(f"Code: {code}  ID: {pid}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Project Type ID details ---\n")
        for pid, code in project_types:
            f.write(f"{code}: {pid}\n")

    with open("output/response.json", "w") as f:
        json.dump(mdms_data, f, indent=2)


@pytest.mark.positive
def test_roles():
    token = get_auth_token("user")
    client = APIClient(token=token)
    response = search_mdms_data(token, client, "ACCESSCONTROL-ROLES.roles")
    assert response.status_code == 200, f"MDMS Search failed: {response.text}"

    mdms_data = response.json().get("mdms", [])
    assert mdms_data, "No Roles data found in response"
    assert all("data" in item and "code" in item["data"] for item in mdms_data), "Missing 'code' in some Roles"
    print("Roles:", [item["data"]["code"] for item in mdms_data])


@pytest.mark.positive
def test_app_config():
    token = get_auth_token("user")
    client = APIClient(token=token)
    response = search_mdms_data(token, client, "HCM.APP_CONFIG")
    assert response.status_code == 200, f"MDMS Search failed: {response.text}"

    mdms_data = response.json().get("mdms", [])
    assert mdms_data, "No App Config data found in response"
    app_config = mdms_data[0].get("data", {})
    print("App Config Dict:")
    for key, value in app_config.items():
        print(f"{key}: {value}")


@pytest.mark.positive
def test_backend_nterface():
    token = get_auth_token("user")
    client = APIClient(token=token)
    response = search_mdms_data(token, client, "HCM.BACKEND_INTERFACE")
    assert response.status_code == 200, f"MDMS Search failed: {response.text}"
    body = response.json()
    # Extract backend interfaces dict
    backend_interfaces = body.get("mdms", [])[0].get("data", {}).get("interfaces", [])
    # Assert presence
    assert backend_interfaces, "No Backend Interfaces found in response"
    # Convert list of dicts into {name: type} or full dict if needed
    interfaces_dict = {iface["name"]: iface for iface in backend_interfaces}
    # Print nicely
    print("Backend Interfaces Dict:")
    for name, iface in interfaces_dict.items():
        print(f"- {name}: type={iface['type']}, config={iface['config']}")


@pytest.mark.positive
def test_state_info():
    token = get_auth_token("user")
    client = APIClient(token=token)
    response = search_mdms_data(token, client, "common-masters.StateInfo")
    assert response.status_code == 200, f"MDMS Search failed: {response.text}"

    body = response.json()

    # Extract state info dict
    state_info = body.get("mdms", [])[0].get("data", {})
    assert state_info, "No StateInfo data found in response"

    # Expected keys in stateInfo
    expected_keys = ["code", "name", "languages", "localizationModules"]
    for key in expected_keys:
        assert key in state_info, f"Missing '{key}' in StateInfo"

    # Print in dictionary style
    print("\nState Info Dict:")
    for key, value in state_info.items():
        print(f"{key}: {value}")


def search_mdms_data(token, client, master_name):
    payload = load_payload("mdms", "search_mdmsData.json")
    payload["MdmsCriteria"]["schemaCode"] = master_name
    payload["RequestInfo"] = get_request_info(token)
    url = f"/{mdms}/v2/_search"
    response = client.post(url, payload)
    return response
