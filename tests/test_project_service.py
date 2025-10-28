from tests.test_mdms_service import get_project_type
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import project



# --- Reusable Functions ---

def create_individual_project(token, client, boundaryType, boundaryCode):
    # projectTypeId=test_project_types
    projectTypeId = extract_id_from_file("MR-DN:")
    payload = load_payload("project", "create_individual_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["projectTypeId"] = projectTypeId
    payload["Projects"][0]["address"]["boundaryType"]=boundaryType
    payload["Projects"][0]["address"]["locality"]["code"]=boundaryCode
    payload["Projects"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["endDate"] = 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"]["id"] = projectTypeId
    payload["Projects"][0]["additionalDetails"]["projectType"] ["cycles"][0]["startDate"]= 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"] ["cycles"][0]["endDate"]= 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"] ["cycles"][1]["startDate"]= 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"] ["cycles"][1]["endDate"]= 1787670131000
    url = f"/{project}/v1/_create"
    response = client.post(url, payload)