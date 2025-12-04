from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import project, boundaryType, boundaryCode


# --- Test functions ---

# def test_create_project():
#     token = get_auth_token("user")
#     client = APIClient(token=token)

#     project_id, status_code = create_individual_project(token, client, boundaryType, boundaryCode)
#     assert status_code in [200, 202], f"Project creation failed with status: {status_code}"

#     print("Project created with ID:", project_id)

#     with open("output/ids.txt", "a") as f:
#         f.write("\n--- Project details ---\n")
#         f.write(f"Project ID: {project_id}\n")


# def test_search_project():
#     token = get_auth_token("user")
#     client = APIClient(token=token)

#     project_id = extract_id_from_file("Project ID:")
#     assert project_id, "Project ID not found in file"

#     projects = search_entity(
#         entity_type="project",
#         token=token,
#         client=client,
#         entity_id=project_id,
#         payload_file="search_project.json",
#         endpoint=f"/{project}/v1/_search",
#         response_key="Project"
#     )

#     assert project_id in [p["id"] for p in projects], "Project not found"
#     print("Project found with ID:", project_id)


# --- Helper function ---

def create_individual_project(token, client, boundaryType, boundaryCode):
    projectTypeId = extract_id_from_file("MR-DN:")
    payload = load_payload("project", "create_individual_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["projectTypeId"] = projectTypeId
    payload["Projects"][0]["address"]["boundaryType"] = boundaryType
    payload["Projects"][0]["address"]["locality"]["code"] = boundaryCode
    payload["Projects"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["endDate"] = 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"]["id"] = projectTypeId
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["endDate"] = 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][1]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][1]["endDate"] = 1787670131000

    url = f"/{project}/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project creation failed with status {response.status_code}: {response.text}")

    project_data = response.json()["Project"][0]
    project_id = project_data["id"]

    return project_id, response.status_code
