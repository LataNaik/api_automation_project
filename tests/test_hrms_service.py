import pytest
import random
import string
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import extract_id_from_file
from utils.config import tenantId, hrms, invalidTenantId


# --- Test functions ---

@pytest.mark.positive
def test_create_employee():
    token = get_auth_token("user")
    client = APIClient(token=token)

    employee_code, username, user_uuid, userservice_uuid, status_code = create_employee(token, client)
    assert status_code in [200, 202], f"Employee creation failed with status: {status_code}"

    print("Employee created with code:", employee_code)
    print("Employee username:", username)
    print("Employee User UUID:", user_uuid)
    print("Employee UserService UUID:", userservice_uuid)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Employee details ---\n")
        f.write(f"Employee Code: {employee_code}\n")
        f.write(f"Employee Username: {username}\n")
        f.write(f"Employee User UUID: {user_uuid}\n")
        f.write(f"Employee UserService UUID: {userservice_uuid}\n")


@pytest.mark.positive
def test_search_employee():
    token = get_auth_token("user")
    client = APIClient(token=token)

    employee_code = extract_id_from_file("Employee Code:")
    assert employee_code, "Employee Code not found in file"

    employees = search_employee(token, client, employee_code)

    assert employee_code in [e["code"] for e in employees], "Employee not found"
    print("Employee found with code:", employee_code)


@pytest.mark.negative
def test_create_hrms_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    payload = load_payload("hrms", "create_hrms.json")
    payload["RequestInfo"] = get_request_info(token)

    # Generate unique code and username
    unique_code = generate_unique_code()
    mobile_number = generate_mobile_number()

    # Update employee code and username
    payload["Employees"][0]["code"] = unique_code
    payload["Employees"][0]["user"]["userName"] = unique_code
    payload["Employees"][0]["user"]["mobileNumber"] = mobile_number

    # Use invalid tenant ID in payload body
    invalid_tenant_id = "invalid.tenant.id"
    payload["Employees"][0]["tenantId"] = invalid_tenant_id
    payload["Employees"][0]["user"]["tenantId"] = invalid_tenant_id

    # Update tenant ID in jurisdictions and roles
    for jurisdiction in payload["Employees"][0].get("jurisdictions", []):
        jurisdiction["tenantId"] = invalid_tenant_id
        for role in jurisdiction.get("roles", []):
            role["tenantId"] = invalid_tenant_id

    # Update tenant ID in user roles
    for role in payload["Employees"][0]["user"].get("roles", []):
        role["tenantId"] = invalid_tenant_id

    url = f"/{hrms}/employees/_create?tenantId={invalid_tenant_id}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_employee_with_invalid_tenant_id():
    """Negative test: Searching employee with invalid tenantId should return error or empty results"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    employee_code = extract_id_from_file("Employee Code:")
    if not employee_code:
        # Create a new employee if code not found
        employee_code, _, _, _, status_code = create_employee(token, client)
        assert status_code in [200, 202], f"Employee creation failed with status: {status_code}"

    payload = load_payload("hrms", "search_hrms.json")
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{hrms}/employees/_search?limit=100&offset=0&tenantId={invalidTenantId}&codes={employee_code}"
    response = client.post(url, payload)

    # API may return error status OR 200 with empty results for invalid tenant
    if response.status_code in [400, 401, 403]:
        print(f"Search correctly rejected with status: {response.status_code}")
    else:
        # If 200, verify employee is not found (empty results due to invalid tenant)
        employees = response.json().get("Employees", [])
        assert employee_code not in [e.get("code") for e in employees], \
            f"Employee should not be found with invalid tenant ID"
        print(f"Search returned empty/filtered results as expected for invalid tenant ID")


# --- Helper functions ---

def generate_unique_code():
    """Generate a unique employee code in format TEST-HRMS-AB-1234"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"TEST-HRMS-{letters}-{numbers}"


def generate_mobile_number():
    """Generate a random 10-digit mobile number"""
    return f"{random.randint(7000000000, 9999999999)}"


def create_employee(token, client):
    payload = load_payload("hrms", "create_hrms.json")
    payload["RequestInfo"] = get_request_info(token)

    # Generate unique code and username
    unique_code = generate_unique_code()
    mobile_number = generate_mobile_number()

    # Update employee code and username
    payload["Employees"][0]["code"] = unique_code
    payload["Employees"][0]["user"]["userName"] = unique_code
    payload["Employees"][0]["user"]["mobileNumber"] = mobile_number

    url = f"/{hrms}/employees/_create?tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Employee creation failed with status {response.status_code}: {response.text}")

    employee_data = response.json()["Employees"][0]
    user_uuid = employee_data["user"]["uuid"]
    userservice_uuid = employee_data["user"]["userServiceUuid"]
    return employee_data["code"], employee_data["user"]["userName"], user_uuid, userservice_uuid, response.status_code


def search_employee(token, client, employee_code):
    payload = load_payload("hrms", "search_hrms.json")
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{hrms}/employees/_search?limit=100&offset=0&tenantId={tenantId}&codes={employee_code}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Employee search failed with status {response.status_code}: {response.text}")

    return response.json().get("Employees", [])
