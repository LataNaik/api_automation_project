import pytest
import json
import random
from datetime import datetime
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import pgr, tenantId, search_limit, search_offset, mdms
from utils.search_helpers import extract_id_from_file


# Load service codes from inputs.json
with open("data/inputs.json", "r") as f:
    inputs_data = json.load(f)


def _fetch_and_update_service_codes():
    """
    Fetch PGR service codes from MDMS at module load time and update inputs.json.
    This runs once when the module is imported.
    """
    try:
        token = get_auth_token("user")
        client = APIClient(token=token)

        payload = load_payload("mdms", "search_mdmsData.json")
        payload["MdmsCriteria"]["schemaCode"] = "RAINMAKER-PGR.ServiceDefs"
        payload["MdmsCriteria"]["tenantId"] = tenantId
        payload["RequestInfo"] = get_request_info(token)

        url = f"/{mdms}/v2/_search"
        response = client.post(url, payload)

        if response.status_code == 200:
            mdms_data = response.json().get("mdms", [])
            if mdms_data:
                # Extract service codes from MDMS response
                service_codes = [item["data"]["serviceCode"] for item in mdms_data if "data" in item and "serviceCode" in item["data"]]
                if service_codes:
                    # Update inputs_data and inputs.json with fetched service codes
                    inputs_data["serviceCode"] = service_codes
                    with open("data/inputs.json", "w") as f:
                        json.dump(inputs_data, f, indent=2)
                    print(f"Fetched {len(service_codes)} service codes from MDMS: {service_codes}")
                    return

        print("Using existing service codes from inputs.json")

    except Exception as e:
        print(f"Warning: Could not fetch service codes from MDMS: {e}. Using existing codes from inputs.json")


# Fetch service codes from MDMS at module load time
_fetch_and_update_service_codes()


# --- Test functions ---

@pytest.mark.positive
def test_create_complaint():
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_complaint(token, client)
    assert res.status_code in [200, 202], f"Complaint creation failed: {res.text}"

    service_wrapper = res.json().get("ServiceWrappers", [])
    assert service_wrapper, "ServiceWrappers not found in response"

    service_request_id = service_wrapper[0]["service"]["serviceRequestId"]
    assert service_request_id, "Service Request ID not found in response"
    print("Complaint created with Service Request ID:", service_request_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- PGR Complaint details ---\n")
        f.write(f"Service Request ID: {service_request_id}\n")


@pytest.mark.positive
def test_resolve_complaint():
    """Test that creates a complaint and then resolves it"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create a complaint
    create_res = create_complaint(token, client)
    assert create_res.status_code in [200, 202], f"Complaint creation failed: {create_res.text}"

    service_wrapper = create_res.json().get("ServiceWrappers", [])
    assert service_wrapper, "ServiceWrappers not found in create response"

    created_service = service_wrapper[0]["service"]
    service_request_id = created_service["serviceRequestId"]
    print(f"Complaint created with Service Request ID: {service_request_id}")

    # Step 2: Resolve the complaint
    resolve_res = resolve_complaint(token, client, created_service)
    assert resolve_res.status_code in [200, 202], f"Complaint resolution failed: {resolve_res.text}"

    resolved_wrapper = resolve_res.json().get("ServiceWrappers", [])
    assert resolved_wrapper, "ServiceWrappers not found in resolve response"

    resolved_status = resolved_wrapper[0]["service"]["applicationStatus"]
    assert resolved_status == "RESOLVED", f"Expected RESOLVED status, got: {resolved_status}"
    print(f"Complaint {service_request_id} resolved successfully with status: {resolved_status}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- PGR Resolved Complaint details ---\n")
        f.write(f"Service Request ID: {service_request_id}\n")
        f.write(f"Status: {resolved_status}\n")


@pytest.mark.positive
def test_search_complaint():
    """Test to search for a complaint by service request ID"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Get service request ID from file
    service_request_id = extract_id_from_file("Service Request ID:")
    assert service_request_id, "Service Request ID not found in file"

    # Search for the complaint
    complaints = search_complaint(token, client, service_request_id)
    assert complaints, "No complaints found in search response"

    # Verify the complaint was found
    found_ids = [c["serviceRequestId"] for c in complaints]
    assert service_request_id in found_ids, f"Complaint {service_request_id} not found in search results"
    print(f"Complaint found with Service Request ID: {service_request_id}")


# --- Reusable Functions ---

def create_complaint(token, client, tenant_id=None, service_code=None):
    """
    Create a PGR complaint.

    Args:
        token: Authentication token
        client: API client instance
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
        service_code: Pass None to use random from pre-fetched codes, or provide specific code

    Returns:
        Response object from the API call
    """
    payload = load_payload("PGR", "create_complaint.json")
    payload["RequestInfo"] = get_request_info(token)

    # Use provided service code or pick random from pre-fetched codes
    if service_code is None:
        service_codes = inputs_data.get("serviceCode", ["SecurityIssues"])
        service_code = random.choice(service_codes)

    payload["service"]["serviceCode"] = service_code
    print(f"Creating complaint with service code: {service_code}")

    # Override tenantId if provided (for negative testing)
    if tenant_id is not None:
        payload["service"]["tenantId"] = tenant_id

    return client.post(f"/{pgr}/v2/request/_create", payload)


def resolve_complaint(token, client, service):
    """
    Resolve a PGR complaint.

    Args:
        token: Authentication token
        client: API client instance
        service: The service object from a created complaint response

    Returns:
        Response object from the API call
    """
    # Extract complaint details from the created service
    complaint_number = service.get("serviceRequestId", "")
    complaint_type = service.get("serviceCode", "")
    application_status = service.get("applicationStatus", "")
    description = service.get("description", "")
    audit_details = service.get("auditDetails", {})

    # Get boundary/area code from address
    address = service.get("address", {})
    locality = address.get("locality", {})
    boundary_code = locality.get("code", "")

    # Format the filed date from audit details
    created_time = audit_details.get("createdTime", 0)
    if created_time:
        filed_date = datetime.fromtimestamp(created_time / 1000).strftime("%d-%b-%Y")
    else:
        filed_date = datetime.now().strftime("%d-%b-%Y")

    # Build the payload with proper complaint details
    payload = {
        "RequestInfo": get_request_info(token),
        "details": {
            "CS_COMPLAINT_DETAILS_COMPLAINT_NO": complaint_number,
            "CS_ADDCOMPLAINT_COMPLAINT_TYPE": f"SERVICEDEFS.{complaint_type}",
            "CS_COMPLAINT_FILED_DATE": filed_date,
            "CS_COMPLAINT_DETAILS_AREA": boundary_code,
            "CS_COMPLAINT_DETAILS_APPLICATION_STATUS": f"CS_COMMON_{application_status}",
            "CS_CREATECOMPLAINT_LANDMARK": address.get("landmark", ""),
            "CS_COMPLAINT_ADDTIONAL_DETAILS": description
        },
        "service": service,
        "workflow": {
            "action": "RESOLVE",
            "comments": "Resolved via automated test",
            "assignes": None,
            "hrmsAssignes": None,
            "verificationDocuments": []
        },
        "audit": {
            "details": audit_details,
            "source": service.get("source", "web"),
            "rating": service.get("rating"),
            "serviceCode": complaint_type
        }
    }

    return client.post(f"/{pgr}/v2/request/_update", payload)


def search_complaint(token, client, service_request_id):
    """
    Search for a PGR complaint by service request ID.

    Args:
        token: Authentication token
        client: API client instance
        service_request_id: The service request ID (complaint number) to search for

    Returns:
        List of services/complaints found
    """
    payload = {
        "RequestInfo": get_request_info(token)
    }

    # Build URL with query parameters
    url = f"/{pgr}/v2/request/_search?serviceRequestId={service_request_id}&tenantId={tenantId}&limit={search_limit}&offset={search_offset}"

    res = client.post(url, payload)
    assert res.status_code == 200, f"Search failed: {res.text}"

    service_wrappers = res.json().get("ServiceWrappers", [])
    return [wrapper["service"] for wrapper in service_wrappers]
