import uuid
import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import project, boundaryType, boundaryCode, tenantId, invalidTenantId
from tests.test_individual_service import create_individual
from tests.test_household_service import create_household, create_household_member
from tests.test_product_service import create_product, create_product_variant
from tests.test_facility_service import create_facility


# --- Test functions ---

@pytest.mark.positive
def test_create_project():
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create first facility
    facility_response_1 = create_facility(token, client)
    assert facility_response_1.status_code in [200, 202], f"Facility 1 creation failed: {facility_response_1.text}"
    facility_id_1 = facility_response_1.json()["Facility"]["id"]

    # Create second facility
    facility_response_2 = create_facility(token, client)
    assert facility_response_2.status_code in [200, 202], f"Facility 2 creation failed: {facility_response_2.text}"
    facility_id_2 = facility_response_2.json()["Facility"]["id"]

    # Create first product variant
    variant_response_1 = create_product_variant(token, client)
    assert variant_response_1.status_code in [200, 202], f"Product Variant 1 creation failed: {variant_response_1.text}"
    variant_id_1 = variant_response_1.json()["ProductVariant"][0]["id"]

    # Create second product variant
    variant_response_2 = create_product_variant(token, client)
    assert variant_response_2.status_code in [200, 202], f"Product Variant 2 creation failed: {variant_response_2.text}"
    variant_id_2 = variant_response_2.json()["ProductVariant"][0]["id"]

    project_id, status_code = create_individual_project(token, client, boundaryType, boundaryCode, variant_id_1, variant_id_2)
    assert status_code in [200, 202], f"Project creation failed with status: {status_code}"

    # Create project resource mapping for first variant
    resource_id_1, resource_status_1 = create_project_resource(token, client, project_id, variant_id_1)
    assert resource_status_1 in [200, 202], f"Project Resource 1 creation failed with status: {resource_status_1}"

    # Create project resource mapping for second variant
    resource_id_2, resource_status_2 = create_project_resource(token, client, project_id, variant_id_2)
    assert resource_status_2 in [200, 202], f"Project Resource 2 creation failed with status: {resource_status_2}"

    # Create project facility mapping for first facility
    project_facility_id_1, facility_status_1 = create_project_facility(token, client, project_id, facility_id_1)
    assert facility_status_1 in [200, 202], f"Project Facility 1 creation failed with status: {facility_status_1}"

    # Create project facility mapping for second facility
    project_facility_id_2, facility_status_2 = create_project_facility(token, client, project_id, facility_id_2)
    assert facility_status_2 in [200, 202], f"Project Facility 2 creation failed with status: {facility_status_2}"

    print("Project created with ID:", project_id)
    print("Project Resource 1 created with ID:", resource_id_1)
    print("Project Resource 2 created with ID:", resource_id_2)
    print("Project Facility 1 created with ID:", project_facility_id_1)
    print("Project Facility 2 created with ID:", project_facility_id_2)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Project details ---\n")
        f.write(f"Project ID: {project_id}\n")
        f.write(f"Project Resource ID 1: {resource_id_1}\n")
        f.write(f"Project Resource ID 2: {resource_id_2}\n")
        f.write(f"Project Facility ID 1: {project_facility_id_1}\n")
        f.write(f"Project Facility ID 2: {project_facility_id_2}\n")


@pytest.mark.positive
def test_search_project():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    assert project_id, "Project ID not found in file"

    projects = search_entity(
        entity_type="project",
        token=token,
        client=client,
        entity_id=project_id,
        payload_file="search_project.json",
        endpoint=f"/{project}/v1/_search",
        response_key="Project"
    )

    assert project_id in [p["id"] for p in projects], "Project not found"
    print("Project found with ID:", project_id)


@pytest.mark.positive
def test_create_project_resource():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    variant_id = extract_id_from_file("Variant ID:")

    assert project_id, "Project ID not found in file"
    assert variant_id, "Variant ID not found in file"

    resource_id, status_code = create_project_resource(token, client, project_id, variant_id)
    assert status_code in [200, 202], f"Project Resource creation failed with status: {status_code}"

    print("Project Resource created with ID:", resource_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Project Resource details ---\n")
        f.write(f"Project Resource ID 1: {resource_id}\n")


@pytest.mark.positive
def test_search_project_resource():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    resource_id = extract_id_from_file("Project Resource ID 1:")

    assert project_id, "Project ID not found in file"
    assert resource_id, "Project Resource ID not found in file"

    resources = search_project_resource(token, client, project_id)

    assert resource_id in [r["id"] for r in resources], "Project Resource not found"
    print("Project Resource found with ID:", resource_id)


@pytest.mark.positive
def test_create_project_staff():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    userservice_uuid = extract_id_from_file("Employee UserService UUID:")

    assert project_id, "Project ID not found in file"
    assert userservice_uuid, "Employee UserService UUID not found in file"

    staff_id, status_code = create_project_staff(token, client, project_id, userservice_uuid)
    assert status_code in [200, 202], f"Project Staff creation failed with status: {status_code}"

    print("Project Staff created with ID:", staff_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Project Staff details ---\n")
        f.write(f"Project Staff ID: {staff_id}\n")


@pytest.mark.positive
def test_search_project_staff():
    token = get_auth_token("user")
    client = APIClient(token=token)

    staff_id = extract_id_from_file("Project Staff ID:")
    assert staff_id, "Project Staff ID not found in file"

    staff_list = search_entity(
        entity_type="project/project_staff",
        token=token,
        client=client,
        entity_id=staff_id,
        payload_file="search_project_staff.json",
        endpoint=f"/{project}/staff/v1/_search",
        response_key="ProjectStaff"
    )

    assert staff_id in [s["id"] for s in staff_list], "Project Staff not found"
    print("Project Staff found with ID:", staff_id)


@pytest.mark.positive
def test_create_project_facility():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    facility_id = extract_id_from_file("Facility ID:")

    assert project_id, "Project ID not found in file"
    assert facility_id, "Facility ID not found in file"

    project_facility_id, status_code = create_project_facility(token, client, project_id, facility_id)
    assert status_code in [200, 202], f"Project Facility creation failed with status: {status_code}"

    print("Project Facility created with ID:", project_facility_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Project Facility details ---\n")
        f.write(f"Project Facility ID: {project_facility_id}\n")


@pytest.mark.positive
def test_search_project_facility():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_facility_id = extract_id_from_file("Project Facility ID:")
    assert project_facility_id, "Project Facility ID not found in file"

    facilities = search_entity(
        entity_type="project/project_facility",
        token=token,
        client=client,
        entity_id=project_facility_id,
        payload_file="search_project_facility.json",
        endpoint=f"/{project}/facility/v1/_search",
        response_key="ProjectFacilities"
    )

    assert project_facility_id in [f["id"] for f in facilities], "Project Facility not found"
    print("Project Facility found with ID:", project_facility_id)


@pytest.mark.negative
def test_create_project_facility_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    facility_id = extract_id_from_file("Facility ID:")

    assert project_id, "Project ID not found in file"
    assert facility_id, "Facility ID not found in file"

    payload = load_payload("project/project_facility", "create_project_facility.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectFacility"]["tenantId"] = "invalid.tenant.id"
    payload["ProjectFacility"]["projectId"] = project_id
    payload["ProjectFacility"]["facilityId"] = facility_id

    url = f"/{project}/facility/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.positive
def test_create_project_beneficiary():
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create new project
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"

    # Create new household
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed with status: {household_status}"

    # Create new individual
    individual_id, individual_client_ref_id, _, individual_status = create_individual(token, client)
    assert individual_status in [200, 202], f"Individual creation failed with status: {individual_status}"

    # Create new household member
    member_response = create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
    assert member_response.status_code in [200, 202], f"Household Member creation failed with status: {member_response.status_code}"

    beneficiary_id, _, status_code = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
    assert status_code in [200, 202], f"Project Beneficiary creation failed with status: {status_code}"

    print("Project Beneficiary created with ID:", beneficiary_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Project Beneficiary details ---\n")
        f.write(f"Project Beneficiary ID: {beneficiary_id}\n")


@pytest.mark.positive
def test_search_project_beneficiary():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_beneficiary_id = extract_id_from_file("Project Beneficiary ID:")
    assert project_beneficiary_id, "Project Beneficiary ID not found in file"

    beneficiaries = search_entity(
        entity_type="project/project_beneficiary",
        token=token,
        client=client,
        entity_id=project_beneficiary_id,
        payload_file="search_project_beneficiary.json",
        endpoint=f"/{project}/beneficiary/v1/_search",
        response_key="ProjectBeneficiaries"
    )

    assert project_beneficiary_id in [b["id"] for b in beneficiaries], "Project Beneficiary not found"
    print("Project Beneficiary found with ID:", project_beneficiary_id)


@pytest.mark.positive
def test_create_project_task():
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create new product variant
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed with status: {variant_response.status_code}"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Create new project with the product variant
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"

    # Create project resource mapping for the variant
    resource_id, resource_status = create_project_resource(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed with status: {resource_status}"

    # Create new household
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed with status: {household_status}"

    # Create new individual
    individual_id, individual_client_ref_id, _, individual_status = create_individual(token, client)
    assert individual_status in [200, 202], f"Individual creation failed with status: {individual_status}"

    # Create new household member
    member_response = create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
    assert member_response.status_code in [200, 202], f"Household Member creation failed with status: {member_response.status_code}"

    # Create new project beneficiary
    beneficiary_id, beneficiary_client_ref_id, beneficiary_status = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
    assert beneficiary_status in [200, 202], f"Project Beneficiary creation failed with status: {beneficiary_status}"

    # Create project task with the mapped product variant
    task_id, task_client_ref_id, status_code = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
    assert status_code in [200, 202], f"Project Task creation failed with status: {status_code}"

    print("Project Task created with ID:", task_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Project Task details ---\n")
        f.write(f"Project Task ID: {task_id}\n")
        f.write(f"Project Task Client Reference ID: {task_client_ref_id}\n")


@pytest.mark.positive
def test_search_project_task():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_task_id = extract_id_from_file("Project Task ID:")
    assert project_task_id, "Project Task ID not found in file"

    tasks = search_entity(
        entity_type="project/project_task",
        token=token,
        client=client,
        entity_id=project_task_id,
        payload_file="search_project_task.json",
        endpoint=f"/{project}/task/v1/_search",
        response_key="Tasks"
    )

    assert project_task_id in [t["id"] for t in tasks], "Project Task not found"
    print("Project Task found with ID:", project_task_id)


@pytest.mark.negative
def test_create_project_task_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    project_beneficiary_id = extract_id_from_file("Project Beneficiary ID:")
    variant_id = extract_id_from_file("Variant ID:")

    assert project_id, "Project ID not found in file"
    assert project_beneficiary_id, "Project Beneficiary ID not found in file"
    assert variant_id, "Variant ID not found in file"

    payload = load_payload("project/project_task", "create_project_task.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Task"]["tenantId"] = "invalid.tenant.id"
    payload["Task"]["projectId"] = project_id
    payload["Task"]["projectBeneficiaryId"] = project_beneficiary_id
    payload["Task"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Task"]["address"]["tenantId"] = "invalid.tenant.id"
    payload["Task"]["address"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Task"]["address"]["locality"]["code"] = boundaryCode
    payload["Task"]["resources"][0]["tenantId"] = "invalid.tenant.id"
    payload["Task"]["resources"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["Task"]["resources"][0]["taskClientReferenceId"] = payload["Task"]["clientReferenceId"]
    payload["Task"]["resources"][0]["productVariantId"] = variant_id

    url = f"/{project}/task/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_create_project_beneficiary_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    individual_id = extract_id_from_file("Individual ID:")
    individual_client_ref_id = extract_id_from_file("Individual Client Reference ID:")

    assert project_id, "Project ID not found in file"
    assert individual_id, "Individual ID not found in file"
    assert individual_client_ref_id, "Individual Client Reference ID not found in file"

    payload = load_payload("project/project_beneficiary", "create_project_beneficiary.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectBeneficiary"]["tenantId"] = "invalid.tenant.id"
    payload["ProjectBeneficiary"]["projectId"] = project_id
    payload["ProjectBeneficiary"]["beneficiaryId"] = individual_id
    payload["ProjectBeneficiary"]["beneficiaryClientReferenceId"] = individual_client_ref_id

    url = f"/{project}/beneficiary/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_create_project_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    projectTypeId = extract_id_from_file("MR-DN:")
    payload = load_payload("project", "create_individual_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["tenantId"] = "invalid.tenant.id"
    payload["Projects"][0]["projectTypeId"] = projectTypeId
    payload["Projects"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["endDate"] = 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"]["id"] = projectTypeId
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["endDate"] = 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][1]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][1]["endDate"] = 1787670131000

    url = f"/{project}/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_create_project_resource_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    variant_id = extract_id_from_file("Variant ID:")

    assert project_id, "Project ID not found in file"
    assert variant_id, "Variant ID not found in file"

    payload = load_payload("project/project_resource", "create_project_resource.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectResource"]["tenantId"] = "invalid.tenant.id"
    payload["ProjectResource"]["projectId"] = project_id
    payload["ProjectResource"]["resource"]["productVariantId"] = variant_id

    url = f"/{project}/resource/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_create_project_staff_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    userservice_uuid = extract_id_from_file("Employee UserService UUID:")

    assert project_id, "Project ID not found in file"
    assert userservice_uuid, "Employee UserService UUID not found in file"

    payload = load_payload("project/project_staff", "create_project_staff.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectStaff"]["tenantId"] = "invalid.tenant.id"
    payload["ProjectStaff"]["projectId"] = project_id
    payload["ProjectStaff"]["userId"] = userservice_uuid

    url = f"/{project}/staff/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_project_with_invalid_tenant_id():
    """Negative test: Searching project with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    if not project_id:
        # Create a new project if ID not found
        project_id, status_code = create_individual_project(token, client, boundaryType, boundaryCode)
        assert status_code in [200, 202], f"Project creation failed with status: {status_code}"

    payload = load_payload("project", "search_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["id"] = project_id

    url = f"/{project}/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_project_resource_with_invalid_tenant_id():
    """Negative test: Searching project resource with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    if not project_id:
        # Create a new project with resource if ID not found
        variant_response = create_product_variant(token, client)
        assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
        variant_id = variant_response.json()["ProductVariant"][0]["id"]
        project_id, status_code = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        assert status_code in [200, 202], f"Project creation failed with status: {status_code}"
        _, resource_status = create_project_resource(token, client, project_id, variant_id)
        assert resource_status in [200, 202], f"Project Resource creation failed"

    payload = load_payload("project/project_resource", "search_project_resource.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectResource"]["projectId"] = [project_id]

    url = f"/{project}/resource/v1/_search?limit=100&offset=0&tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_project_staff_with_invalid_tenant_id():
    """Negative test: Searching project staff with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    staff_id = extract_id_from_file("Project Staff ID:")
    if not staff_id:
        # Create project and staff if not found
        project_id = extract_id_from_file("Project ID:")
        userservice_uuid = extract_id_from_file("Employee UserService UUID:")
        if not project_id:
            project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode)
        if not userservice_uuid:
            from tests.test_hrms_service import create_employee
            _, _, _, userservice_uuid, _ = create_employee(token, client)
        staff_id, _ = create_project_staff(token, client, project_id, userservice_uuid)

    payload = load_payload("project/project_staff", "search_project_staff.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectStaff"]["id"] = [staff_id]

    url = f"/{project}/staff/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_project_facility_with_invalid_tenant_id():
    """Negative test: Searching project facility with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_facility_id = extract_id_from_file("Project Facility ID:")
    if not project_facility_id:
        # Create project and facility if not found
        project_id = extract_id_from_file("Project ID:")
        facility_id = extract_id_from_file("Facility ID:")
        if not project_id:
            project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode)
        if not facility_id:
            facility_response = create_facility(token, client)
            assert facility_response.status_code in [200, 202], f"Facility creation failed"
            facility_id = facility_response.json()["Facility"]["id"]
        project_facility_id, _ = create_project_facility(token, client, project_id, facility_id)

    payload = load_payload("project/project_facility", "search_project_facility.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectFacility"]["id"] = [project_facility_id]

    url = f"/{project}/facility/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_project_beneficiary_with_invalid_tenant_id():
    """Negative test: Searching project beneficiary with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    beneficiary_id = extract_id_from_file("Project Beneficiary ID:")
    if not beneficiary_id:
        # Create project and beneficiary if not found
        project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode)
        household_id, household_client_ref_id, _ = create_household(token, client)
        individual_id, individual_client_ref_id, _, _ = create_individual(token, client)
        create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
        beneficiary_id, _, _ = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)

    payload = load_payload("project/project_beneficiary", "search_project_beneficiary.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectBeneficiary"]["id"] = [beneficiary_id]

    url = f"/{project}/beneficiary/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_project_task_with_invalid_tenant_id():
    """Negative test: Searching project task with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    task_id = extract_id_from_file("Project Task ID:")
    if not task_id:
        # Create project, beneficiary, and task if not found
        variant_response = create_product_variant(token, client)
        assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
        variant_id = variant_response.json()["ProductVariant"][0]["id"]
        project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        create_project_resource(token, client, project_id, variant_id)
        household_id, household_client_ref_id, _ = create_household(token, client)
        individual_id, individual_client_ref_id, _, _ = create_individual(token, client)
        create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
        beneficiary_id, beneficiary_client_ref_id, _ = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
        task_id, _, _ = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)

    payload = load_payload("project/project_task", "search_project_task.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Task"]["id"] = [task_id]

    url = f"/{project}/task/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


# --- Helper functions ---

def create_individual_project(token, client, boundaryType, boundaryCode, variant_id_1=None, variant_id_2=None):
    projectTypeId = extract_id_from_file("MR-DN:")
    payload = load_payload("project", "create_individual_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["projectTypeId"] = projectTypeId
    # payload["Projects"][0]["address"]["boundaryType"] = boundaryType
    # payload["Projects"][0]["address"]["locality"]["code"] = boundaryCode
    payload["Projects"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["endDate"] = 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"]["id"] = projectTypeId
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["endDate"] = 1787670131000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][1]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][1]["endDate"] = 1787670131000

    # Set product variant IDs if provided
    if variant_id_1 is not None and variant_id_2 is not None:
        # Update resources
        payload["Projects"][0]["additionalDetails"]["projectType"]["resources"][0]["productVariantId"] = variant_id_1
        payload["Projects"][0]["additionalDetails"]["projectType"]["resources"][1]["productVariantId"] = variant_id_2

        # Update product variants in cycles' deliveries' doseCriteria
        for cycle in payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"]:
            for delivery in cycle.get("deliveries", []):
                for dose in delivery.get("doseCriteria", []):
                    for i, pv in enumerate(dose.get("ProductVariants", [])):
                        if i == 0:
                            pv["productVariantId"] = variant_id_1
                        elif i == 1:
                            pv["productVariantId"] = variant_id_2

    url = f"/{project}/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project creation failed with status {response.status_code}: {response.text}")

    project_data = response.json()["Project"][0]
    project_id = project_data["id"]

    return project_id, response.status_code


def create_project_resource(token, client, project_id, variant_id):
    payload = load_payload("project/project_resource", "create_project_resource.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectResource"]["tenantId"] = tenantId
    payload["ProjectResource"]["projectId"] = project_id
    payload["ProjectResource"]["resource"]["productVariantId"] = variant_id

    url = f"/{project}/resource/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Resource creation failed with status {response.status_code}: {response.text}")

    resource_data = response.json()["ProjectResource"]
    resource_id = resource_data["id"]

    return resource_id, response.status_code


def search_project_resource(token, client, project_id):
    payload = load_payload("project/project_resource", "search_project_resource.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectResource"]["projectId"] = [project_id]

    url = f"/{project}/resource/v1/_search?limit=100&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code != 200:
        raise Exception(f"Project Resource search failed with status {response.status_code}: {response.text}")

    return response.json().get("ProjectResources", [])


def create_project_staff(token, client, project_id, userservice_uuid):
    payload = load_payload("project/project_staff", "create_project_staff.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectStaff"]["tenantId"] = tenantId
    payload["ProjectStaff"]["projectId"] = project_id
    payload["ProjectStaff"]["userId"] = userservice_uuid

    url = f"/{project}/staff/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Staff creation failed with status {response.status_code}: {response.text}")

    staff_data = response.json()["ProjectStaff"]
    return staff_data["id"], response.status_code


def create_project_facility(token, client, project_id, facility_id):
    payload = load_payload("project/project_facility", "create_project_facility.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectFacility"]["tenantId"] = tenantId
    payload["ProjectFacility"]["projectId"] = project_id
    payload["ProjectFacility"]["facilityId"] = facility_id

    url = f"/{project}/facility/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Facility creation failed with status {response.status_code}: {response.text}")

    facility_data = response.json()["ProjectFacility"]
    return facility_data["id"], response.status_code


def create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id):
    payload = load_payload("project/project_beneficiary", "create_project_beneficiary.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectBeneficiary"]["tenantId"] = tenantId
    payload["ProjectBeneficiary"]["projectId"] = project_id
    payload["ProjectBeneficiary"]["beneficiaryId"] = individual_id
    payload["ProjectBeneficiary"]["beneficiaryClientReferenceId"] = individual_client_ref_id
    payload["ProjectBeneficiary"]["clientReferenceId"] = str(uuid.uuid4())

    url = f"/{project}/beneficiary/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Beneficiary creation failed with status {response.status_code}: {response.text}")

    beneficiary_data = response.json()["ProjectBeneficiary"]
    return beneficiary_data["id"], beneficiary_data["clientReferenceId"], response.status_code


def create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id):
    payload = load_payload("project/project_task", "create_project_task.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Task"]["tenantId"] = tenantId
    payload["Task"]["projectId"] = project_id
    payload["Task"]["projectBeneficiaryId"] = beneficiary_id
    payload["Task"]["projectBeneficiaryClientReferenceId"] = beneficiary_client_ref_id
    payload["Task"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Task"]["address"]["tenantId"] = tenantId
    payload["Task"]["address"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Task"]["address"]["locality"]["code"] = boundaryCode
    payload["Task"]["resources"][0]["tenantId"] = tenantId
    payload["Task"]["resources"][0]["clientReferenceId"] = str(uuid.uuid4())
    payload["Task"]["resources"][0]["taskClientReferenceId"] = payload["Task"]["clientReferenceId"]
    payload["Task"]["resources"][0]["productVariantId"] = variant_id

    url = f"/{project}/task/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Task creation failed with status {response.status_code}: {response.text}")

    task_data = response.json()["Task"]
    return task_data["id"], task_data["clientReferenceId"], response.status_code
