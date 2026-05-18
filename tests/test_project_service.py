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
def test_create_individual_project():
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
def test_search_individual_project():
    """Test to search for a project by ID. Creates project if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    if not project_id:
        # Create project internally if ID not found
        print("Project ID not found in file, creating new project...")
        project_id, status_code = create_individual_project(token, client, boundaryType, boundaryCode)
        assert status_code in [200, 202], f"Project creation failed with status: {status_code}"
        print(f"Project created with ID: {project_id}")

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
    """Test to search for a project resource by ID. Creates project and resource if not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    resource_id = extract_id_from_file("Project Resource ID 1:")

    if not project_id or not resource_id:
        # Create project and resource internally if not found
        print("Project/Resource ID not found in file, creating new project with resource...")
        variant_response = create_product_variant(token, client)
        assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
        variant_id = variant_response.json()["ProductVariant"][0]["id"]
        project_id, status_code = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        assert status_code in [200, 202], f"Project creation failed with status: {status_code}"
        resource_id, resource_status = create_project_resource(token, client, project_id, variant_id)
        assert resource_status in [200, 202], f"Project Resource creation failed with status: {resource_status}"
        print(f"Project created with ID: {project_id}, Resource ID: {resource_id}")

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
    """Test to search for a project staff by ID. Creates project staff if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    staff_id = extract_id_from_file("Project Staff ID:")
    if not staff_id:
        # Create project staff internally if not found
        print("Project Staff ID not found in file, creating new project staff...")
        project_id = extract_id_from_file("Project ID:")
        userservice_uuid = extract_id_from_file("Employee UserService UUID:")
        if not project_id:
            project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode)
        if not userservice_uuid:
            from tests.test_hrms_service import create_employee
            _, _, _, userservice_uuid, _ = create_employee(token, client)
        staff_id, staff_status = create_project_staff(token, client, project_id, userservice_uuid)
        assert staff_status in [200, 202], f"Project Staff creation failed with status: {staff_status}"
        print(f"Project Staff created with ID: {staff_id}")

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
    """Test to search for a project facility by ID. Creates project facility if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_facility_id = extract_id_from_file("Project Facility ID:")
    if not project_facility_id:
        # Create project facility internally if not found
        print("Project Facility ID not found in file, creating new project facility...")
        project_id = extract_id_from_file("Project ID:")
        facility_id = extract_id_from_file("Facility ID:")
        if not project_id:
            project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode)
        if not facility_id:
            facility_response = create_facility(token, client)
            assert facility_response.status_code in [200, 202], f"Facility creation failed"
            facility_id = facility_response.json()["Facility"]["id"]
        project_facility_id, status = create_project_facility(token, client, project_id, facility_id)
        assert status in [200, 202], f"Project Facility creation failed with status: {status}"
        print(f"Project Facility created with ID: {project_facility_id}")

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
    """Test to search for a project beneficiary by ID. Creates project beneficiary if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_beneficiary_id = extract_id_from_file("Project Beneficiary ID:")
    if not project_beneficiary_id:
        # Create project beneficiary internally if not found
        print("Project Beneficiary ID not found in file, creating new project beneficiary...")
        project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode)
        household_id, household_client_ref_id, _ = create_household(token, client)
        individual_id, individual_client_ref_id, _, _ = create_individual(token, client)
        create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
        project_beneficiary_id, _, status = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
        assert status in [200, 202], f"Project Beneficiary creation failed with status: {status}"
        print(f"Project Beneficiary created with ID: {project_beneficiary_id}")

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
    """Test to search for a project task by ID. Creates project task if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_task_id = extract_id_from_file("Project Task ID:")
    if not project_task_id:
        # Create project task with all dependencies if not found
        print("Project Task ID not found in file, creating project task with dependencies...")
        variant_response = create_product_variant(token, client)
        assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
        variant_id = variant_response.json()["ProductVariant"][0]["id"]
        project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        create_project_resource(token, client, project_id, variant_id)
        household_id, household_client_ref_id, _ = create_household(token, client)
        individual_id, individual_client_ref_id, _, _ = create_individual(token, client)
        create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
        beneficiary_id, beneficiary_client_ref_id, _ = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
        project_task_id, _, status = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
        assert status in [200, 202], f"Project Task creation failed with status: {status}"
        print(f"Project Task created with ID: {project_task_id}")

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
def test_create_individual_project_with_invalid_tenant_id():
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
def test_search_individual_project_with_invalid_tenant_id():
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


@pytest.mark.positive
def test_update_project_beneficiary():
    """Test to update a project beneficiary. Creates all dependencies internally first, then updates the tag."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating project for update test...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
    print(f"Project created with ID: {project_id}")

    print("Creating household...")
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed with status: {household_status}"

    print("Creating individual...")
    individual_id, individual_client_ref_id, _, individual_status = create_individual(token, client)
    assert individual_status in [200, 202], f"Individual creation failed with status: {individual_status}"

    print("Creating household member...")
    member_response = create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
    assert member_response.status_code in [200, 202], f"Household Member creation failed"

    print("Creating project beneficiary...")
    beneficiary_id, beneficiary_client_ref_id, beneficiary_status = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
    assert beneficiary_status in [200, 202], f"Project Beneficiary creation failed with status: {beneficiary_status}"
    print(f"Project Beneficiary created with ID: {beneficiary_id}")

    # Step 2: Search for the beneficiary to get full data for update
    beneficiaries = search_project_beneficiary(token, client, beneficiary_id)
    assert len(beneficiaries) > 0, "Could not find created project beneficiary"
    beneficiary_data = beneficiaries[0]
    original_tag = beneficiary_data.get("tag", "")
    print(f"Original tag: '{original_tag}'")

    # Step 3: Update the beneficiary (change tag)
    new_tag = f"UPDATED-TAG-{str(uuid.uuid4())[:8]}"
    response = update_project_beneficiary(token, client, beneficiary_data, new_tag)
    assert response.status_code in [200, 202], f"Project Beneficiary update failed: {response.text}"

    # Step 4: Verify update
    updated_beneficiary = response.json()["ProjectBeneficiary"]
    assert updated_beneficiary["tag"] == new_tag, f"Tag not updated. Expected {new_tag}, got {updated_beneficiary.get('tag')}"
    print(f"Project Beneficiary updated successfully. Tag changed from '{original_tag}' to '{new_tag}'")


@pytest.mark.positive
def test_update_project_task():
    """Test to update a project task. Creates all dependencies internally first, then updates the status."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
    print(f"Project created with ID: {project_id}")

    print("Creating project resource...")
    resource_id, resource_status = create_project_resource(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed"

    print("Creating household...")
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed"

    print("Creating individual...")
    individual_id, individual_client_ref_id, _, individual_status = create_individual(token, client)
    assert individual_status in [200, 202], f"Individual creation failed"

    print("Creating household member...")
    member_response = create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
    assert member_response.status_code in [200, 202], f"Household Member creation failed"

    print("Creating project beneficiary...")
    beneficiary_id, beneficiary_client_ref_id, beneficiary_status = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
    assert beneficiary_status in [200, 202], f"Project Beneficiary creation failed"

    print("Creating project task...")
    task_id, task_client_ref_id, task_status = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
    assert task_status in [200, 202], f"Project Task creation failed with status: {task_status}"
    print(f"Project Task created with ID: {task_id}")

    # Step 2: Search for the task to get full data for update
    tasks = search_project_task(token, client, task_id)
    assert len(tasks) > 0, "Could not find created project task"
    task_data = tasks[0]
    original_status = task_data.get("status", "")
    print(f"Original status: '{original_status}'")

    # Step 3: Update the task (change status)
    new_status = "ADMINISTRATION_SUCCESS"
    response = update_project_task(token, client, task_data, new_status)
    assert response.status_code in [200, 202], f"Project Task update failed: {response.text}"

    # Step 4: Verify update
    updated_task = response.json()["Task"]
    assert updated_task["status"] == new_status, f"Status not updated. Expected {new_status}, got {updated_task.get('status')}"
    print(f"Project Task updated successfully. Status changed from '{original_status}' to '{new_status}'")


@pytest.mark.positive
def test_update_individual_project():
    """Test to update a project. Creates project internally first, then updates the description."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create project internally
    print("Creating product variants...")
    variant_response_1 = create_product_variant(token, client)
    assert variant_response_1.status_code in [200, 202], f"Product Variant 1 creation failed"
    variant_id_1 = variant_response_1.json()["ProductVariant"][0]["id"]

    variant_response_2 = create_product_variant(token, client)
    assert variant_response_2.status_code in [200, 202], f"Product Variant 2 creation failed"
    variant_id_2 = variant_response_2.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_data, project_status = create_individual_project_full(token, client, boundaryType, boundaryCode, variant_id_1, variant_id_2)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
    print(f"Project created with ID: {project_data['id']}")

    # Step 2: Use create response data directly
    original_description = project_data.get("description", "")
    print(f"Original description: {original_description}")

    # Step 3: Update the project (change description)
    new_description = f"Updated description via automated test - {str(uuid.uuid4())[:8]}"
    response = update_project(token, client, project_data, new_description)
    assert response.status_code in [200, 202], f"Project update failed: {response.text}"

    # Step 4: Verify update
    updated_project = response.json()["Project"][0]
    assert updated_project["description"] == new_description, f"Description not updated. Expected {new_description}, got {updated_project.get('description')}"
    print(f"Project updated successfully. Description changed from '{original_description}' to '{new_description}'")


@pytest.mark.positive
def test_update_project_staff():
    """Test to update a project staff. Creates all dependencies internally first, then updates the endDate."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
    print(f"Project created with ID: {project_id}")

    print("Creating employee...")
    from tests.test_hrms_service import create_employee
    _, _, _, userservice_uuid, employee_status = create_employee(token, client)
    assert employee_status in [200, 202], f"Employee creation failed"
    print(f"Employee created with userServiceUuid: {userservice_uuid}")

    print("Creating project staff...")
    staff_data, staff_status = create_project_staff_full(token, client, project_id, userservice_uuid)
    assert staff_status in [200, 202], f"Project Staff creation failed with status: {staff_status}"
    print(f"Project Staff created with ID: {staff_data['id']}")

    # Step 2: Use create response data directly
    original_end_date = staff_data.get("endDate", 0)
    print(f"Original endDate: {original_end_date}")

    # Step 3: Update the project staff (change endDate)
    new_end_date = 9999999999999
    response = update_project_staff(token, client, staff_data, new_end_date)
    assert response.status_code in [200, 202], f"Project Staff update failed: {response.text}"

    # Step 4: Verify update
    updated_staff = response.json()["ProjectStaff"]
    assert updated_staff["endDate"] == new_end_date, f"EndDate not updated. Expected {new_end_date}, got {updated_staff.get('endDate')}"
    print(f"Project Staff updated successfully. EndDate changed from {original_end_date} to {new_end_date}")


@pytest.mark.positive
def test_update_project_resource():
    """Test to update a project resource. Creates all dependencies internally first, then updates the resource type."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
    print(f"Project created with ID: {project_id}")

    print("Creating project resource...")
    resource_data, resource_status = create_project_resource_full(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed with status: {resource_status}"
    print(f"Project Resource created with ID: {resource_data['id']}")

    # Step 2: Use create response data directly
    original_type = resource_data.get("resource", {}).get("type", "")
    print(f"Original resource type: {original_type}")

    # Step 3: Update the project resource (change resource type)
    new_type = "BEDNET"
    response = update_project_resource(token, client, resource_data, new_type)
    assert response.status_code in [200, 202], f"Project Resource update failed: {response.text}"

    # Step 4: Verify update
    updated_resource = response.json()["ProjectResource"]
    assert updated_resource["resource"]["type"] == new_type, f"Resource type not updated. Expected {new_type}, got {updated_resource.get('resource', {}).get('type')}"
    print(f"Project Resource updated successfully. Resource type changed from '{original_type}' to '{new_type}'")


@pytest.mark.positive
def test_update_project_facility():
    """Test to update a project facility. Creates all dependencies internally first, then updates additionalFields."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
    print(f"Project created with ID: {project_id}")

    print("Creating facility...")
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed"
    facility_id = facility_response.json()["Facility"]["id"]
    print(f"Facility created with ID: {facility_id}")

    print("Creating project facility...")
    project_facility_data, project_facility_status = create_project_facility_full(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility creation failed with status: {project_facility_status}"
    print(f"Project Facility created with ID: {project_facility_data['id']}")

    # Step 2: Use create response data directly
    original_additional = project_facility_data.get("additionalFields", {})
    print(f"Original additionalFields: {original_additional}")

    # Step 3: Update the project facility (add additionalFields)
    new_additional_fields = {
        "schema": "updated_schema",
        "version": 2,
        "fields": [
            {"key": "updated_key", "value": "updated_value"}
        ]
    }
    response = update_project_facility(token, client, project_facility_data, new_additional_fields)
    assert response.status_code in [200, 202], f"Project Facility update failed: {response.text}"

    # Step 4: Verify update
    updated_facility = response.json()["ProjectFacility"]
    assert updated_facility.get("additionalFields", {}).get("schema") == "updated_schema", f"AdditionalFields not updated correctly"
    print(f"Project Facility updated successfully. AdditionalFields updated.")


@pytest.mark.positive
def test_delete_project_facility():
    """Test to delete a project facility. Uses existing project if available, creates mapping fresh, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Use existing project ID or create new one
    project_id = extract_id_from_file("Project ID:")
    if project_id:
        print(f"Using existing Project ID: {project_id}")
    else:
        print("No existing project found, creating new project...")
        project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode)
        assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
        print(f"Project created with ID: {project_id}")

    print("Creating facility...")
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed"
    facility_id = facility_response.json()["Facility"]["id"]
    print(f"Facility created with ID: {facility_id}")

    print("Creating project facility...")
    project_facility_data, project_facility_status = create_project_facility_full(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility creation failed with status: {project_facility_status}"
    project_facility_id = project_facility_data['id']
    print(f"Project Facility created with ID: {project_facility_id}")

    # Step 2: Delete the project facility
    print("Deleting project facility...")
    response = delete_project_facility(token, client, project_facility_data)
    assert response.status_code in [200, 202], f"Project Facility delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_facility = response.json()["ProjectFacility"]
    assert deleted_facility["isDeleted"] == True, f"Project Facility not marked as deleted"
    print(f"Project Facility {project_facility_id} deleted successfully")


@pytest.mark.positive
def test_delete_project_resource():
    """Test to delete a project resource. Uses existing project if available, creates mapping fresh, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create product variant (always needed for resource)
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Use existing project ID or create new one
    project_id = extract_id_from_file("Project ID:")
    if project_id:
        print(f"Using existing Project ID: {project_id}")
    else:
        print("No existing project found, creating new project...")
        project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
        print(f"Project created with ID: {project_id}")

    print("Creating project resource...")
    resource_data, resource_status = create_project_resource_full(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed with status: {resource_status}"
    resource_id = resource_data['id']
    print(f"Project Resource created with ID: {resource_id}")

    # Step 2: Delete the project resource
    print("Deleting project resource...")
    response = delete_project_resource(token, client, resource_data)
    assert response.status_code in [200, 202], f"Project Resource delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_resource = response.json()["ProjectResource"]
    assert deleted_resource["isDeleted"] == True, f"Project Resource not marked as deleted"
    print(f"Project Resource {resource_id} deleted successfully")


@pytest.mark.positive
def test_delete_project_staff():
    """Test to delete a project staff. Uses existing project if available, creates mapping fresh, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Use existing project ID or create new one
    project_id = extract_id_from_file("Project ID:")
    if project_id:
        print(f"Using existing Project ID: {project_id}")
    else:
        print("No existing project found, creating new project...")
        project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode)
        assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
        print(f"Project created with ID: {project_id}")

    print("Creating employee...")
    from tests.test_hrms_service import create_employee
    _, _, _, userservice_uuid, employee_status = create_employee(token, client)
    assert employee_status in [200, 202], f"Employee creation failed"
    print(f"Employee created with userServiceUuid: {userservice_uuid}")

    print("Creating project staff...")
    staff_data, staff_status = create_project_staff_full(token, client, project_id, userservice_uuid)
    assert staff_status in [200, 202], f"Project Staff creation failed with status: {staff_status}"
    staff_id = staff_data['id']
    print(f"Project Staff created with ID: {staff_id}")

    # Step 2: Delete the project staff
    print("Deleting project staff...")
    response = delete_project_staff(token, client, staff_data)
    assert response.status_code in [200, 202], f"Project Staff delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_staff = response.json()["ProjectStaff"]
    assert deleted_staff["isDeleted"] == True, f"Project Staff not marked as deleted"
    print(f"Project Staff {staff_id} deleted successfully")


@pytest.mark.positive
def test_delete_project_beneficiary():
    """Test to delete a project beneficiary. Uses existing project if available, creates mapping fresh, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Use existing project ID or create new one
    project_id = extract_id_from_file("Project ID:")
    if project_id:
        print(f"Using existing Project ID: {project_id}")
    else:
        print("No existing project found, creating new project...")
        project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode)
        assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
        print(f"Project created with ID: {project_id}")

    print("Creating household...")
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed with status: {household_status}"

    print("Creating individual...")
    individual_id, individual_client_ref_id, _, individual_status = create_individual(token, client)
    assert individual_status in [200, 202], f"Individual creation failed with status: {individual_status}"

    print("Creating household member...")
    member_response = create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
    assert member_response.status_code in [200, 202], f"Household Member creation failed"

    print("Creating project beneficiary...")
    beneficiary_data, beneficiary_status = create_project_beneficiary_full(token, client, project_id, individual_id, individual_client_ref_id)
    assert beneficiary_status in [200, 202], f"Project Beneficiary creation failed with status: {beneficiary_status}"
    beneficiary_id = beneficiary_data['id']
    print(f"Project Beneficiary created with ID: {beneficiary_id}")

    # Step 2: Delete the project beneficiary
    print("Deleting project beneficiary...")
    response = delete_project_beneficiary(token, client, beneficiary_data)
    assert response.status_code in [200, 202], f"Project Beneficiary delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_beneficiary = response.json()["ProjectBeneficiary"]
    assert deleted_beneficiary["isDeleted"] == True, f"Project Beneficiary not marked as deleted"
    print(f"Project Beneficiary {beneficiary_id} deleted successfully")


@pytest.mark.positive
def test_delete_project_task():
    """Test to delete a project task. Uses existing project if available, creates mapping fresh, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create product variant (always needed for task)
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Use existing project ID or create new one
    project_id = extract_id_from_file("Project ID:")
    if project_id:
        print(f"Using existing Project ID: {project_id}")
    else:
        print("No existing project found, creating new project...")
        project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
        print(f"Project created with ID: {project_id}")

    print("Creating project resource...")
    resource_id, resource_status = create_project_resource(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed"

    print("Creating household...")
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed"

    print("Creating individual...")
    individual_id, individual_client_ref_id, _, individual_status = create_individual(token, client)
    assert individual_status in [200, 202], f"Individual creation failed"

    print("Creating household member...")
    member_response = create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
    assert member_response.status_code in [200, 202], f"Household Member creation failed"

    print("Creating project beneficiary...")
    beneficiary_id, beneficiary_client_ref_id, beneficiary_status = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
    assert beneficiary_status in [200, 202], f"Project Beneficiary creation failed"

    print("Creating project task...")
    task_data, task_status = create_project_task_full(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
    assert task_status in [200, 202], f"Project Task creation failed with status: {task_status}"
    task_id = task_data['id']
    print(f"Project Task created with ID: {task_id}")

    # Step 2: Delete the project task
    print("Deleting project task...")
    response = delete_project_task(token, client, task_data)
    assert response.status_code in [200, 202], f"Project Task delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_task = response.json()["Task"]
    assert deleted_task["isDeleted"] == True, f"Project Task not marked as deleted"
    print(f"Project Task {task_id} deleted successfully")


# --- Household Project Tests ---

@pytest.mark.positive
def test_create_household_project():
    """Test creating a household (Bednet) project with facility, variant, and resources."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create facility
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed: {facility_response.text}"
    facility_id = facility_response.json()["Facility"]["id"]

    # Create product variant
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed: {variant_response.text}"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Create household project
    project_id, status_code = create_household_project(token, client, boundaryType, boundaryCode, variant_id)
    assert status_code in [200, 202], f"Household Project creation failed with status: {status_code}"

    # Create project resource mapping
    resource_id, resource_status = create_project_resource(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed with status: {resource_status}"

    # Create project facility mapping
    project_facility_id, facility_status = create_project_facility(token, client, project_id, facility_id)
    assert facility_status in [200, 202], f"Project Facility creation failed with status: {facility_status}"

    print("Household Project created with ID:", project_id)
    print("Project Resource created with ID:", resource_id)
    print("Project Facility created with ID:", project_facility_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Household Project details ---\n")
        f.write(f"Household Project ID: {project_id}\n")
        f.write(f"Household Project Resource ID: {resource_id}\n")
        f.write(f"Household Project Facility ID: {project_facility_id}\n")


@pytest.mark.positive
def test_search_household_project():
    """Test to search for a household (Bednet) project by ID."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Household Project ID:")
    if not project_id:
        print("Household Project ID not found in file, creating new household project...")
        project_id, status_code = create_household_project(token, client, boundaryType, boundaryCode)
        assert status_code in [200, 202], f"Household Project creation failed with status: {status_code}"
        print(f"Household Project created with ID: {project_id}")

    projects = search_entity(
        entity_type="project",
        token=token,
        client=client,
        entity_id=project_id,
        payload_file="search_project.json",
        endpoint=f"/{project}/v1/_search",
        response_key="Project"
    )

    assert project_id in [p["id"] for p in projects], "Household Project not found"
    print("Household Project found with ID:", project_id)


@pytest.mark.positive
def test_update_household_project():
    """Test to update a household (Bednet) project. Creates project internally first, then updates the description."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create product variant
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Step 2: Create household project
    print("Creating household project...")
    project_data, project_status = create_household_project_full(token, client, boundaryType, boundaryCode, variant_id)
    assert project_status in [200, 202], f"Household Project creation failed with status: {project_status}"
    print(f"Household Project created with ID: {project_data['id']}")

    # Step 3: Use create response data directly
    original_description = project_data.get("description", "")
    print(f"Original description: {original_description}")

    # Step 4: Update the project (change description)
    new_description = f"Updated household project description via automated test - {str(uuid.uuid4())[:8]}"
    response = update_project(token, client, project_data, new_description)
    assert response.status_code in [200, 202], f"Household Project update failed: {response.text}"

    # Step 5: Verify update
    updated_project = response.json()["Project"][0]
    assert updated_project["description"] == new_description, f"Description not updated. Expected {new_description}, got {updated_project.get('description')}"
    print(f"Household Project updated successfully. Description changed from '{original_description}' to '{new_description}'")


@pytest.mark.positive
def test_create_household_project_beneficiary():
    """Test creating a project beneficiary using household ID for a household (Bednet) project."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create household project
    project_id, project_status = create_household_project(token, client, boundaryType, boundaryCode)
    assert project_status in [200, 202], f"Household Project creation failed with status: {project_status}"

    # Create household
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed with status: {household_status}"

    # Create beneficiary with household as the beneficiary entity
    beneficiary_id, _, status_code = create_household_project_beneficiary(token, client, project_id, household_id, household_client_ref_id)
    assert status_code in [200, 202], f"Household Project Beneficiary creation failed with status: {status_code}"

    print("Household Project Beneficiary created with ID:", beneficiary_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Household Project Beneficiary details ---\n")
        f.write(f"Household Project Beneficiary ID: {beneficiary_id}\n")


@pytest.mark.positive
def test_search_household_project_beneficiary():
    """Test to search for a household project beneficiary by ID."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    beneficiary_id = extract_id_from_file("Household Project Beneficiary ID:")
    if not beneficiary_id:
        print("Household Project Beneficiary ID not found in file, creating new...")
        project_id, _ = create_household_project(token, client, boundaryType, boundaryCode)
        household_id, household_client_ref_id, _ = create_household(token, client)
        beneficiary_id, _, status = create_household_project_beneficiary(token, client, project_id, household_id, household_client_ref_id)
        assert status in [200, 202], f"Household Project Beneficiary creation failed with status: {status}"
        print(f"Household Project Beneficiary created with ID: {beneficiary_id}")

    beneficiaries = search_entity(
        entity_type="project/project_beneficiary",
        token=token,
        client=client,
        entity_id=beneficiary_id,
        payload_file="search_project_beneficiary.json",
        endpoint=f"/{project}/beneficiary/v1/_search",
        response_key="ProjectBeneficiaries"
    )

    assert beneficiary_id in [b["id"] for b in beneficiaries], "Household Project Beneficiary not found"
    print("Household Project Beneficiary found with ID:", beneficiary_id)


@pytest.mark.positive
def test_update_household_project_beneficiary():
    """Test to update a household project beneficiary. Creates all dependencies internally first, then updates the tag."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating household project...")
    project_id, project_status = create_household_project(token, client, boundaryType, boundaryCode)
    assert project_status in [200, 202], f"Household Project creation failed with status: {project_status}"
    print(f"Household Project created with ID: {project_id}")

    print("Creating household...")
    household_id, household_client_ref_id, household_status = create_household(token, client)
    assert household_status in [200, 202], f"Household creation failed with status: {household_status}"

    print("Creating household project beneficiary...")
    beneficiary_id, _, beneficiary_status = create_household_project_beneficiary(token, client, project_id, household_id, household_client_ref_id)
    assert beneficiary_status in [200, 202], f"Household Project Beneficiary creation failed with status: {beneficiary_status}"
    print(f"Household Project Beneficiary created with ID: {beneficiary_id}")

    # Step 2: Search for the beneficiary to get full data for update
    beneficiaries = search_project_beneficiary(token, client, beneficiary_id)
    assert len(beneficiaries) > 0, "Could not find created household project beneficiary"
    beneficiary_data = beneficiaries[0]
    original_tag = beneficiary_data.get("tag", "")
    print(f"Original tag: '{original_tag}'")

    # Step 3: Update the beneficiary (change tag)
    new_tag = f"HH-UPDATED-TAG-{str(uuid.uuid4())[:8]}"
    response = update_project_beneficiary(token, client, beneficiary_data, new_tag)
    assert response.status_code in [200, 202], f"Household Project Beneficiary update failed: {response.text}"

    # Step 4: Verify update
    updated_beneficiary = response.json()["ProjectBeneficiary"]
    assert updated_beneficiary["tag"] == new_tag, f"Tag not updated. Expected {new_tag}, got {updated_beneficiary.get('tag')}"
    print(f"Household Project Beneficiary updated successfully. Tag changed from '{original_tag}' to '{new_tag}'")


@pytest.mark.negative
def test_create_household_project_with_invalid_tenant_id():
    """Negative test: Creating household project with invalid tenantId should fail."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    projectTypeId = extract_id_from_file("Bednet:")
    payload = load_payload("project", "create_household_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["tenantId"] = "invalid.tenant.id"
    payload["Projects"][0]["projectTypeId"] = projectTypeId
    payload["Projects"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["endDate"] = 1798707420000
    payload["Projects"][0]["additionalDetails"]["projectType"]["id"] = projectTypeId
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["endDate"] = 1798707420000

    url = f"/{project}/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_household_project_with_invalid_tenant_id():
    """Negative test: Searching household project with invalid tenantId should fail."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Household Project ID:")
    if not project_id:
        project_id, status_code = create_household_project(token, client, boundaryType, boundaryCode)
        assert status_code in [200, 202], f"Household Project creation failed with status: {status_code}"

    payload = load_payload("project", "search_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["id"] = project_id

    url = f"/{project}/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


# --- Helper functions ---

def create_individual_project(token, client, boundaryType, boundaryCode, variant_id_1=None, variant_id_2=None):
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


def search_project_beneficiary(token, client, beneficiary_id):
    """Search for a project beneficiary by ID and return full data."""
    payload = load_payload("project/project_beneficiary", "search_project_beneficiary.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectBeneficiary"]["id"] = [beneficiary_id]

    url = f"/{project}/beneficiary/v1/_search?limit=100&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Beneficiary search failed with status {response.status_code}: {response.text}")

    return response.json().get("ProjectBeneficiaries", [])


def search_project_task(token, client, task_id):
    """Search for a project task by ID and return full data."""
    payload = load_payload("project/project_task", "search_project_task.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Task"]["id"] = [task_id]

    url = f"/{project}/task/v1/_search?limit=100&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Task search failed with status {response.status_code}: {response.text}")

    return response.json().get("Tasks", [])


def update_project_beneficiary(token, client, beneficiary_data, new_tag):
    """
    Update a project beneficiary's tag.

    Args:
        beneficiary_data: Full project beneficiary object from search
        new_tag: New tag value to set
    """
    payload = load_payload("project/project_beneficiary", "update_project_beneficiary.json")

    # Copy required fields from the searched beneficiary
    payload["ProjectBeneficiary"]["id"] = beneficiary_data["id"]
    payload["ProjectBeneficiary"]["tenantId"] = beneficiary_data["tenantId"]
    payload["ProjectBeneficiary"]["clientReferenceId"] = beneficiary_data["clientReferenceId"]
    payload["ProjectBeneficiary"]["rowVersion"] = beneficiary_data["rowVersion"]
    payload["ProjectBeneficiary"]["auditDetails"] = beneficiary_data["auditDetails"]
    payload["ProjectBeneficiary"]["clientAuditDetails"] = beneficiary_data.get("clientAuditDetails")
    payload["ProjectBeneficiary"]["projectId"] = beneficiary_data["projectId"]
    payload["ProjectBeneficiary"]["beneficiaryId"] = beneficiary_data["beneficiaryId"]
    payload["ProjectBeneficiary"]["beneficiaryClientReferenceId"] = beneficiary_data["beneficiaryClientReferenceId"]
    payload["ProjectBeneficiary"]["dateOfRegistration"] = beneficiary_data.get("dateOfRegistration")
    payload["ProjectBeneficiary"]["tag"] = new_tag
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/beneficiary/v1/_update"
    response = client.post(url, payload)
    return response


def update_project_task(token, client, task_data, new_status):
    """
    Update a project task's status.

    Args:
        task_data: Full project task object from search
        new_status: New status value to set
    """
    payload = load_payload("project/project_task", "update_project_task.json")

    # Copy required fields from the searched task
    payload["Task"]["id"] = task_data["id"]
    payload["Task"]["tenantId"] = task_data["tenantId"]
    payload["Task"]["clientReferenceId"] = task_data["clientReferenceId"]
    payload["Task"]["rowVersion"] = task_data["rowVersion"]
    payload["Task"]["auditDetails"] = task_data["auditDetails"]
    payload["Task"]["clientAuditDetails"] = task_data.get("clientAuditDetails")
    payload["Task"]["projectId"] = task_data["projectId"]
    payload["Task"]["projectBeneficiaryId"] = task_data["projectBeneficiaryId"]
    payload["Task"]["projectBeneficiaryClientReferenceId"] = task_data.get("projectBeneficiaryClientReferenceId")
    payload["Task"]["resources"] = task_data.get("resources", [])
    payload["Task"]["address"] = task_data.get("address")
    payload["Task"]["status"] = new_status
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/task/v1/_update"
    response = client.post(url, payload)
    return response


def create_project_staff_full(token, client, project_id, userservice_uuid):
    """
    Create a project staff and return full data for update operations.

    Returns:
        Tuple of (staff_data, status_code)
    """
    payload = load_payload("project/project_staff", "create_project_staff.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectStaff"]["tenantId"] = tenantId
    payload["ProjectStaff"]["projectId"] = project_id
    payload["ProjectStaff"]["userId"] = userservice_uuid

    url = f"/{project}/staff/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Staff creation failed with status {response.status_code}: {response.text}")

    return response.json()["ProjectStaff"], response.status_code


def create_project_resource_full(token, client, project_id, variant_id):
    """
    Create a project resource and return full data for update operations.

    Returns:
        Tuple of (resource_data, status_code)
    """
    payload = load_payload("project/project_resource", "create_project_resource.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectResource"]["tenantId"] = tenantId
    payload["ProjectResource"]["projectId"] = project_id
    payload["ProjectResource"]["resource"]["productVariantId"] = variant_id

    url = f"/{project}/resource/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Resource creation failed with status {response.status_code}: {response.text}")

    return response.json()["ProjectResource"], response.status_code


def create_project_facility_full(token, client, project_id, facility_id):
    """
    Create a project facility and return full data for update operations.

    Returns:
        Tuple of (facility_data, status_code)
    """
    payload = load_payload("project/project_facility", "create_project_facility.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectFacility"]["tenantId"] = tenantId
    payload["ProjectFacility"]["projectId"] = project_id
    payload["ProjectFacility"]["facilityId"] = facility_id

    url = f"/{project}/facility/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Project Facility creation failed with status {response.status_code}: {response.text}")

    return response.json()["ProjectFacility"], response.status_code


def update_project_staff(token, client, staff_data, new_end_date):
    """
    Update a project staff's endDate.

    Args:
        staff_data: Full project staff object from create response
        new_end_date: New endDate value to set
    """
    payload = load_payload("project/project_staff", "update_project_staff.json")

    # Copy required fields from the created staff
    payload["ProjectStaff"]["id"] = staff_data["id"]
    payload["ProjectStaff"]["tenantId"] = staff_data["tenantId"]
    payload["ProjectStaff"]["rowVersion"] = staff_data["rowVersion"]
    payload["ProjectStaff"]["auditDetails"] = staff_data["auditDetails"]
    payload["ProjectStaff"]["userId"] = staff_data["userId"]
    payload["ProjectStaff"]["projectId"] = staff_data["projectId"]
    payload["ProjectStaff"]["startDate"] = staff_data.get("startDate")
    payload["ProjectStaff"]["endDate"] = new_end_date
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/staff/v1/_update"
    response = client.post(url, payload)
    return response


def update_project_resource(token, client, resource_data, new_type):
    """
    Update a project resource's type.

    Args:
        resource_data: Full project resource object from create response
        new_type: New resource type value to set
    """
    payload = load_payload("project/project_resource", "update_project_resource.json")

    # Copy required fields from the created resource
    payload["ProjectResource"]["id"] = resource_data["id"]
    payload["ProjectResource"]["tenantId"] = resource_data["tenantId"]
    payload["ProjectResource"]["rowVersion"] = resource_data["rowVersion"]
    payload["ProjectResource"]["auditDetails"] = resource_data["auditDetails"]
    payload["ProjectResource"]["projectId"] = resource_data["projectId"]
    payload["ProjectResource"]["resource"] = resource_data["resource"].copy()
    payload["ProjectResource"]["resource"]["type"] = new_type
    payload["ProjectResource"]["startDate"] = resource_data.get("startDate")
    payload["ProjectResource"]["endDate"] = resource_data.get("endDate")
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/resource/v1/_update"
    response = client.post(url, payload)
    return response


def update_project_facility(token, client, facility_data, new_additional_fields):
    """
    Update a project facility's additionalFields.

    Args:
        facility_data: Full project facility object from create response
        new_additional_fields: New additionalFields value to set
    """
    payload = load_payload("project/project_facility", "update_project_facility.json")

    # Copy required fields from the created facility
    payload["ProjectFacility"]["id"] = facility_data["id"]
    payload["ProjectFacility"]["tenantId"] = facility_data["tenantId"]
    payload["ProjectFacility"]["rowVersion"] = facility_data["rowVersion"]
    payload["ProjectFacility"]["auditDetails"] = facility_data["auditDetails"]
    payload["ProjectFacility"]["facilityId"] = facility_data["facilityId"]
    payload["ProjectFacility"]["projectId"] = facility_data["projectId"]
    payload["ProjectFacility"]["additionalFields"] = new_additional_fields
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/facility/v1/_update"
    response = client.post(url, payload)
    return response


def create_individual_project_full(token, client, boundaryType, boundaryCode, variant_id_1=None, variant_id_2=None):
    """
    Create a project and return full data for update operations.

    Returns:
        Tuple of (project_data, status_code)
    """
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

    return response.json()["Project"][0], response.status_code


def update_project(token, client, project_data, new_description):
    """
    Update a project's description.

    Args:
        project_data: Full project object from create response
        new_description: New description value to set
    """
    payload = load_payload("project", "update_project.json")

    # Copy required fields from the created project
    payload["Projects"][0]["id"] = project_data["id"]
    payload["Projects"][0]["tenantId"] = project_data["tenantId"]
    payload["Projects"][0]["projectNumber"] = project_data.get("projectNumber")
    payload["Projects"][0]["name"] = project_data.get("name")
    payload["Projects"][0]["projectType"] = project_data.get("projectType")
    payload["Projects"][0]["projectSubType"] = project_data.get("projectSubType")
    payload["Projects"][0]["department"] = project_data.get("department")
    payload["Projects"][0]["description"] = new_description
    payload["Projects"][0]["referenceID"] = project_data.get("referenceID")
    payload["Projects"][0]["projectTypeId"] = project_data.get("projectTypeId")
    payload["Projects"][0]["address"] = project_data.get("address")
    payload["Projects"][0]["startDate"] = project_data.get("startDate")
    payload["Projects"][0]["endDate"] = project_data.get("endDate")
    payload["Projects"][0]["isTaskEnabled"] = project_data.get("isTaskEnabled", False)
    payload["Projects"][0]["targets"] = project_data.get("targets", [])
    payload["Projects"][0]["additionalDetails"] = project_data.get("additionalDetails")
    payload["Projects"][0]["rowVersion"] = project_data.get("rowVersion", 0)
    payload["Projects"][0]["auditDetails"] = project_data.get("auditDetails")
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/v1/_update"
    response = client.post(url, payload)
    return response


def delete_project_facility(token, client, facility_data):
    """
    Delete a project facility (soft delete by setting isDeleted=true).

    Args:
        facility_data: Full project facility object from create response
    """
    payload = load_payload("project/project_facility", "delete_project_facility.json")

    # Copy required fields from the created facility
    payload["ProjectFacility"]["id"] = facility_data["id"]
    payload["ProjectFacility"]["tenantId"] = facility_data["tenantId"]
    payload["ProjectFacility"]["rowVersion"] = facility_data["rowVersion"]
    payload["ProjectFacility"]["auditDetails"] = facility_data["auditDetails"]
    payload["ProjectFacility"]["facilityId"] = facility_data["facilityId"]
    payload["ProjectFacility"]["projectId"] = facility_data["projectId"]
    payload["ProjectFacility"]["additionalFields"] = facility_data.get("additionalFields")
    payload["ProjectFacility"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/facility/v1/_delete"
    response = client.post(url, payload)
    return response


def delete_project_resource(token, client, resource_data):
    """
    Delete a project resource (soft delete by setting isDeleted=true).

    Args:
        resource_data: Full project resource object from create response
    """
    payload = load_payload("project/project_resource", "delete_project_resource.json")

    # Copy required fields from the created resource
    payload["ProjectResource"]["id"] = resource_data["id"]
    payload["ProjectResource"]["tenantId"] = resource_data["tenantId"]
    payload["ProjectResource"]["rowVersion"] = resource_data["rowVersion"]
    payload["ProjectResource"]["auditDetails"] = resource_data["auditDetails"]
    payload["ProjectResource"]["projectId"] = resource_data["projectId"]
    payload["ProjectResource"]["resource"] = resource_data["resource"]
    payload["ProjectResource"]["startDate"] = resource_data.get("startDate")
    payload["ProjectResource"]["endDate"] = resource_data.get("endDate")
    payload["ProjectResource"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/resource/v1/_delete"
    response = client.post(url, payload)
    return response


def delete_project_staff(token, client, staff_data):
    """
    Delete a project staff (soft delete by setting isDeleted=true).

    Args:
        staff_data: Full project staff object from create response
    """
    payload = load_payload("project/project_staff", "delete_project_staff.json")

    # Copy required fields from the created staff
    payload["ProjectStaff"]["id"] = staff_data["id"]
    payload["ProjectStaff"]["tenantId"] = staff_data["tenantId"]
    payload["ProjectStaff"]["rowVersion"] = staff_data["rowVersion"]
    payload["ProjectStaff"]["auditDetails"] = staff_data["auditDetails"]
    payload["ProjectStaff"]["userId"] = staff_data["userId"]
    payload["ProjectStaff"]["projectId"] = staff_data["projectId"]
    payload["ProjectStaff"]["startDate"] = staff_data.get("startDate")
    payload["ProjectStaff"]["endDate"] = staff_data.get("endDate")
    payload["ProjectStaff"]["additionalFields"] = staff_data.get("additionalFields")
    payload["ProjectStaff"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/staff/v1/_delete"
    response = client.post(url, payload)
    return response


def create_project_beneficiary_full(token, client, project_id, individual_id, individual_client_ref_id):
    """
    Create a project beneficiary and return full data for delete operations.

    Returns:
        Tuple of (beneficiary_data, status_code)
    """
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

    return response.json()["ProjectBeneficiary"], response.status_code


def create_project_task_full(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id):
    """
    Create a project task and return full data for delete operations.

    Returns:
        Tuple of (task_data, status_code)
    """
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

    return response.json()["Task"], response.status_code


def delete_project_beneficiary(token, client, beneficiary_data):
    """
    Delete a project beneficiary (soft delete by setting isDeleted=true).

    Args:
        beneficiary_data: Full project beneficiary object from create response
    """
    payload = load_payload("project/project_beneficiary", "delete_project_beneficiary.json")

    # Copy required fields from the created beneficiary
    payload["ProjectBeneficiary"]["id"] = beneficiary_data["id"]
    payload["ProjectBeneficiary"]["tenantId"] = beneficiary_data["tenantId"]
    payload["ProjectBeneficiary"]["clientReferenceId"] = beneficiary_data["clientReferenceId"]
    payload["ProjectBeneficiary"]["rowVersion"] = beneficiary_data["rowVersion"]
    payload["ProjectBeneficiary"]["auditDetails"] = beneficiary_data["auditDetails"]
    payload["ProjectBeneficiary"]["clientAuditDetails"] = beneficiary_data.get("clientAuditDetails")
    payload["ProjectBeneficiary"]["projectId"] = beneficiary_data["projectId"]
    payload["ProjectBeneficiary"]["beneficiaryId"] = beneficiary_data["beneficiaryId"]
    payload["ProjectBeneficiary"]["beneficiaryClientReferenceId"] = beneficiary_data["beneficiaryClientReferenceId"]
    payload["ProjectBeneficiary"]["dateOfRegistration"] = beneficiary_data.get("dateOfRegistration")
    payload["ProjectBeneficiary"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/beneficiary/v1/_delete"
    response = client.post(url, payload)
    return response


def delete_project_task(token, client, task_data):
    """
    Delete a project task (soft delete by setting isDeleted=true).

    Args:
        task_data: Full project task object from create response
    """
    payload = load_payload("project/project_task", "delete_project_task.json")

    # Copy required fields from the created task
    payload["Task"]["id"] = task_data["id"]
    payload["Task"]["tenantId"] = task_data["tenantId"]
    payload["Task"]["clientReferenceId"] = task_data["clientReferenceId"]
    payload["Task"]["rowVersion"] = task_data["rowVersion"]
    payload["Task"]["auditDetails"] = task_data["auditDetails"]
    payload["Task"]["clientAuditDetails"] = task_data.get("clientAuditDetails")
    payload["Task"]["projectId"] = task_data["projectId"]
    payload["Task"]["projectBeneficiaryId"] = task_data["projectBeneficiaryId"]
    payload["Task"]["projectBeneficiaryClientReferenceId"] = task_data.get("projectBeneficiaryClientReferenceId")
    payload["Task"]["resources"] = task_data.get("resources", [])
    payload["Task"]["address"] = task_data.get("address")
    payload["Task"]["status"] = task_data.get("status")
    payload["Task"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{project}/task/v1/_delete"
    response = client.post(url, payload)
    return response


def create_household_project(token, client, boundaryType, boundaryCode, variant_id=None):
    """
    Create a household (Bednet) project and return (project_id, status_code).
    """
    projectTypeId = extract_id_from_file("Bednet:")
    payload = load_payload("project", "create_household_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["projectTypeId"] = projectTypeId
    payload["Projects"][0]["address"]["boundaryType"] = boundaryType
    payload["Projects"][0]["address"]["boundary"] = boundaryCode
    payload["Projects"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["endDate"] = 1798707420000
    payload["Projects"][0]["additionalDetails"]["projectType"]["id"] = projectTypeId
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["endDate"] = 1798707420000

    # Set product variant ID if provided
    if variant_id is not None:
        payload["Projects"][0]["additionalDetails"]["projectType"]["resources"][0]["productVariantId"] = variant_id
        for cycle in payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"]:
            for delivery in cycle.get("deliveries", []):
                for dose in delivery.get("doseCriteria", []):
                    for pv in dose.get("ProductVariants", []):
                        pv["productVariantId"] = variant_id

    url = f"/{project}/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Household Project creation failed with status {response.status_code}: {response.text}")

    project_data = response.json()["Project"][0]
    return project_data["id"], response.status_code


def create_household_project_full(token, client, boundaryType, boundaryCode, variant_id=None):
    """
    Create a household (Bednet) project and return full project data for update operations.

    Returns:
        Tuple of (project_data, status_code)
    """
    projectTypeId = extract_id_from_file("Bednet:")
    payload = load_payload("project", "create_household_project.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Projects"][0]["projectTypeId"] = projectTypeId
    payload["Projects"][0]["address"]["boundaryType"] = boundaryType
    payload["Projects"][0]["address"]["boundary"] = boundaryCode
    payload["Projects"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["endDate"] = 1798707420000
    payload["Projects"][0]["additionalDetails"]["projectType"]["id"] = projectTypeId
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["startDate"] = 1767205799000
    payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"][0]["endDate"] = 1798707420000

    # Set product variant ID if provided
    if variant_id is not None:
        payload["Projects"][0]["additionalDetails"]["projectType"]["resources"][0]["productVariantId"] = variant_id
        for cycle in payload["Projects"][0]["additionalDetails"]["projectType"]["cycles"]:
            for delivery in cycle.get("deliveries", []):
                for dose in delivery.get("doseCriteria", []):
                    for pv in dose.get("ProductVariants", []):
                        pv["productVariantId"] = variant_id

    url = f"/{project}/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Household Project creation failed with status {response.status_code}: {response.text}")

    return response.json()["Project"][0], response.status_code


def create_household_project_beneficiary(token, client, project_id, household_id, household_client_ref_id):
    """
    Create a project beneficiary using a household ID (for household/Bednet project type).

    Returns:
        Tuple of (beneficiary_id, client_reference_id, status_code)
    """
    payload = load_payload("project/project_beneficiary", "create_project_beneficiary.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProjectBeneficiary"]["tenantId"] = tenantId
    payload["ProjectBeneficiary"]["projectId"] = project_id
    payload["ProjectBeneficiary"]["beneficiaryId"] = household_id
    payload["ProjectBeneficiary"]["beneficiaryClientReferenceId"] = household_client_ref_id
    payload["ProjectBeneficiary"]["clientReferenceId"] = str(uuid.uuid4())

    url = f"/{project}/beneficiary/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Household Project Beneficiary creation failed with status {response.status_code}: {response.text}")

    beneficiary_data = response.json()["ProjectBeneficiary"]
    return beneficiary_data["id"], beneficiary_data["clientReferenceId"], response.status_code
