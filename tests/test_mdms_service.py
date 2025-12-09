import pytest
import json
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import extract_id_from_file
from utils.config import mdms, tenantId


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


@pytest.mark.positive
def test_create_schema_definition():
    token = get_auth_token("user")
    client = APIClient(token=token)

    schema_code, status_code = create_schema_definition(token, client)
    assert status_code in [200, 202], f"Schema Definition creation failed with status: {status_code}"

    print("Schema Definition created with code:", schema_code)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Schema Definition details ---\n")
        f.write(f"Schema Code: {schema_code}\n")


@pytest.mark.positive
def test_search_schema_definition():
    token = get_auth_token("user")
    client = APIClient(token=token)

    schema_code = extract_id_from_file("Schema Code:")
    assert schema_code, "Schema Code not found in file"

    schemas = search_schema_definition(token, client, schema_code)

    assert schema_code in [s["code"] for s in schemas], "Schema Definition not found"
    print("Schema Definition found with code:", schema_code)


@pytest.mark.positive
def test_add_mdms_data():
    token = get_auth_token("user")
    client = APIClient(token=token)

    schema_code = extract_id_from_file("Schema Code:")
    assert schema_code, "Schema Code not found in file"

    mdms_id, status_code = add_mdms_data(token, client, schema_code)
    assert status_code in [200, 202], f"MDMS Data creation failed with status: {status_code}"

    print("MDMS Data added with ID:", mdms_id)

    with open("output/ids.txt", "a") as f:
        f.write(f"MDMS Data ID: {mdms_id}\n")


@pytest.mark.positive
def test_search_added_mdms_data():
    token = get_auth_token("user")
    client = APIClient(token=token)

    schema_code = extract_id_from_file("Schema Code:")
    mdms_id = extract_id_from_file("MDMS Data ID:")

    assert schema_code, "Schema Code not found in file"
    assert mdms_id, "MDMS Data ID not found in file"

    mdms_records = search_mdms_by_schema(token, client, schema_code)

    assert mdms_id in [r["id"] for r in mdms_records], "MDMS Data not found"
    print("MDMS Data found with ID:", mdms_id)


# --- Helper functions ---

def search_mdms_data(token, client, master_name):
    payload = load_payload("mdms", "search_mdmsData.json")
    payload["MdmsCriteria"]["schemaCode"] = master_name
    payload["RequestInfo"] = get_request_info(token)
    url = f"/{mdms}/v2/_search"
    response = client.post(url, payload)
    return response


def get_next_schema_code(token, client):
    """Get the next schema code by searching existing schemas in the API"""
    for i in range(1, 1000):
        code = f"Test.Schema.{i}"
        payload = load_payload("mdms", "search_schema_definitions.json")
        payload["RequestInfo"] = get_request_info(token)
        payload["SchemaDefCriteria"]["tenantId"] = tenantId
        payload["SchemaDefCriteria"]["codes"] = [code]

        url = f"/{mdms}/schema/v1/_search"
        response = client.post(url, payload)
        schemas = response.json().get("SchemaDefinitions", [])

        if not schemas:
            return code
    return "Test.Schema.1"


def create_schema_definition(token, client):
    payload = load_payload("mdms", "create_schema_definition.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SchemaDefinition"]["tenantId"] = tenantId

    # Generate unique schema code by searching existing ones
    schema_code = get_next_schema_code(token, client)
    payload["SchemaDefinition"]["code"] = schema_code

    url = f"/{mdms}/schema/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Schema Definition creation failed with status {response.status_code}: {response.text}")

    schema_data = response.json()["SchemaDefinitions"][0]
    return schema_data["code"], response.status_code


def search_schema_definition(token, client, schema_code):
    payload = load_payload("mdms", "search_schema_definitions.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SchemaDefCriteria"]["tenantId"] = tenantId
    payload["SchemaDefCriteria"]["codes"] = [schema_code]

    url = f"/{mdms}/schema/v1/_search"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Schema Definition search failed with status {response.status_code}: {response.text}")

    return response.json().get("SchemaDefinitions", [])


def get_next_mdms_data_id(token, client, schema_code):
    """Get the next MDMS data ID by searching existing data in the schema"""
    response = search_mdms_data(token, client, schema_code)
    mdms_records = response.json().get("mdms", [])

    if not mdms_records:
        return "1"

    # Find the highest existing id and increment
    existing_ids = []
    for record in mdms_records:
        data_id = record.get("data", {}).get("id", "0")
        try:
            existing_ids.append(int(data_id))
        except ValueError:
            continue

    if existing_ids:
        return str(max(existing_ids) + 1)
    return "1"


def add_mdms_data(token, client, schema_code):
    payload = load_payload("mdms", "add_mdmdData.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Mdms"]["tenantId"] = tenantId
    payload["Mdms"]["schemaCode"] = schema_code

    # Generate unique data ID
    data_id = get_next_mdms_data_id(token, client, schema_code)
    payload["Mdms"]["data"]["id"] = data_id

    url = f"/{mdms}/v2/_create/{schema_code}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"MDMS Data creation failed with status {response.status_code}: {response.text}")

    mdms_record = response.json()["Mdms"]
    return mdms_record["id"], response.status_code


def search_mdms_by_schema(token, client, schema_code):
    payload = load_payload("mdms", "search_mdmsData.json")
    payload["MdmsCriteria"]["schemaCode"] = schema_code
    payload["MdmsCriteria"]["tenantId"] = tenantId
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{mdms}/v2/_search"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"MDMS Data search failed with status {response.status_code}: {response.text}")

    return response.json().get("mdms", [])
