import uuid
import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import tenantId, boundaryType, boundaryCode, project
from tests.test_individual_service import create_individual
from tests.test_household_service import create_household, create_household_member
from tests.test_product_service import create_product_variant
from tests.test_project_service import (
    create_individual_project,
    create_project_resource,
    create_project_beneficiary,
    create_project_task,
    create_project_facility
)
from tests.test_facility_service import create_facility


# --- Test functions ---

@pytest.mark.positive
def test_create_side_effect():
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create new product variant
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed: {variant_response.status_code}"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Create new project with the product variant
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"

    # Create project resource mapping for the variant
    _, resource_status = create_project_resource(token, client, project_id, variant_id)
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

    # Create project task
    task_id, task_client_ref_id, task_status = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
    assert task_status in [200, 202], f"Project Task creation failed with status: {task_status}"

    # Create side effect
    side_effect_id, _, status_code = create_side_effect(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)
    assert status_code in [200, 202], f"Side Effect creation failed with status: {status_code}"

    print("Side Effect created with ID:", side_effect_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Side Effect details ---\n")
        f.write(f"Side Effect ID: {side_effect_id}\n")


@pytest.mark.positive
def test_search_side_effect():
    """Test to search for a side effect by ID. Uses existing side effect if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    side_effect_id = extract_id_from_file("Side Effect ID:")
    if not side_effect_id:
        # Use existing side effect from system (async create takes too long to be searchable)
        print("Side Effect ID not found in file, fetching existing side effect...")
        existing_side_effects = search_side_effect_all(token, client)
        assert existing_side_effects, "No existing Side Effects found in system"
        side_effect_id = existing_side_effects[0]["id"]
        print(f"Using existing Side Effect ID: {side_effect_id}")

    side_effects = search_entity(
        entity_type="referralmanagement/side_effect",
        token=token,
        client=client,
        entity_id=side_effect_id,
        payload_file="search_side_effect.json",
        endpoint=f"/referralmanagement/side-effect/v1/_search",
        response_key="SideEffects"
    )

    assert side_effect_id in [s["id"] for s in side_effects], "Side Effect not found"
    print("Side Effect found with ID:", side_effect_id)


@pytest.mark.positive
def test_create_referral():
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create new product variant
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed: {variant_response.status_code}"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Create new project with the product variant
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"

    # Create project resource mapping for the variant
    _, resource_status = create_project_resource(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed with status: {resource_status}"

    # Create facility and map to project
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed: {facility_response.status_code}"
    facility_id = facility_response.json()["Facility"]["id"]

    # Create project facility mapping
    _, project_facility_status = create_project_facility(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility mapping failed with status: {project_facility_status}"

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

    # Create project task
    task_id, task_client_ref_id, task_status = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
    assert task_status in [200, 202], f"Project Task creation failed with status: {task_status}"

    # Create side effect
    side_effect_id, side_effect_client_ref_id, side_effect_status = create_side_effect(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)
    assert side_effect_status in [200, 202], f"Side Effect creation failed with status: {side_effect_status}"

    # Create referral using side effect details and mapped facility
    referral_id, status_code = create_referral(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id, side_effect_id, side_effect_client_ref_id, facility_id)
    assert status_code in [200, 202], f"Referral creation failed with status: {status_code}"

    print("Referral created with ID:", referral_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Referral details ---\n")
        f.write(f"Referral ID: {referral_id}\n")


@pytest.mark.positive
def test_search_referral():
    """Test to search for a referral by ID. Uses existing referral if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    referral_id = extract_id_from_file("Referral ID:")
    if not referral_id:
        # Use existing referral from system (async create takes too long to be searchable)
        print("Referral ID not found in file, fetching existing referral...")
        existing_referrals = search_referral_all(token, client)
        assert existing_referrals, "No existing Referrals found in system"
        referral_id = existing_referrals[0]["id"]
        print(f"Using existing Referral ID: {referral_id}")

    referrals = search_entity(
        entity_type="referralmanagement/referral",
        token=token,
        client=client,
        entity_id=referral_id,
        payload_file="search_referral.json",
        endpoint=f"/referralmanagement/v1/_search",
        response_key="Referrals"
    )

    assert referral_id in [r["id"] for r in referrals], "Referral not found"
    print("Referral found with ID:", referral_id)


@pytest.mark.positive
def test_create_hf_referral():
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Create new product variant
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed: {variant_response.status_code}"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    # Create new project with the product variant
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"

    # Create facility
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed: {facility_response.status_code}"
    facility_id = facility_response.json()["Facility"]["id"]

    # Create project facility mapping
    project_facility_id, project_facility_status = create_project_facility(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility mapping failed with status: {project_facility_status}"

    # Create HF Referral
    hf_referral_id, status_code = create_hf_referral(token, client, project_id, project_facility_id)
    assert status_code in [200, 202], f"HF Referral creation failed with status: {status_code}"

    print("HF Referral created with ID:", hf_referral_id)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- HF Referral details ---\n")
        f.write(f"HF Referral ID: {hf_referral_id}\n")


@pytest.mark.positive
def test_search_hf_referral():
    """Test to search for an HF referral by ID. Uses existing HF referral if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    hf_referral_id = extract_id_from_file("HF Referral ID:")
    if not hf_referral_id:
        # Use existing HF referral from system (async create takes too long to be searchable)
        print("HF Referral ID not found in file, fetching existing HF referral...")
        existing_hf_referrals = search_hf_referral_all(token, client)
        assert existing_hf_referrals, "No existing HF Referrals found in system"
        hf_referral_id = existing_hf_referrals[0]["id"]
        print(f"Using existing HF Referral ID: {hf_referral_id}")

    hf_referrals = search_entity(
        entity_type="referralmanagement/hf_referral",
        token=token,
        client=client,
        entity_id=hf_referral_id,
        payload_file="search_hf_referral.json",
        endpoint=f"/referralmanagement/hf-referral/v1/_search",
        response_key="HFReferrals"
    )

    assert hf_referral_id in [r["id"] for r in hf_referrals], "HF Referral not found"
    print("HF Referral found with ID:", hf_referral_id)


@pytest.mark.negative
def test_create_side_effect_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    task_id = extract_id_from_file("Project Task ID:")
    task_client_ref_id = extract_id_from_file("Project Task Client Reference ID:")
    beneficiary_id = extract_id_from_file("Project Beneficiary ID:")

    assert task_id, "Project Task ID not found in file"
    assert task_client_ref_id, "Project Task Client Reference ID not found in file"
    assert beneficiary_id, "Project Beneficiary ID not found in file"

    payload = load_payload("referralmanagement/side_effect", "create_side_effect.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SideEffect"]["tenantId"] = "invalid.tenant.id"
    payload["SideEffect"]["clientReferenceId"] = str(uuid.uuid4())
    payload["SideEffect"]["taskId"] = task_id
    payload["SideEffect"]["taskClientReferenceId"] = task_client_ref_id
    payload["SideEffect"]["projectBeneficiaryId"] = beneficiary_id
    payload["SideEffect"]["projectBeneficiaryClientReferenceId"] = str(uuid.uuid4())
    payload["SideEffect"]["symptoms"] = ["FEVER", "VOMITING"]

    url = f"/{project}/side-effect/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_create_referral_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    task_id = extract_id_from_file("Project Task ID:")
    task_client_ref_id = extract_id_from_file("Project Task Client Reference ID:")
    beneficiary_id = extract_id_from_file("Project Beneficiary ID:")
    side_effect_id = extract_id_from_file("Side Effect ID:")

    assert task_id, "Project Task ID not found in file"
    assert task_client_ref_id, "Project Task Client Reference ID not found in file"
    assert beneficiary_id, "Project Beneficiary ID not found in file"
    assert side_effect_id, "Side Effect ID not found in file"

    payload = load_payload("referralmanagement/referral", "create_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Referral"]["tenantId"] = "invalid.tenant.id"
    payload["Referral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Referral"]["taskId"] = task_id
    payload["Referral"]["taskClientReferenceId"] = task_client_ref_id
    payload["Referral"]["projectBeneficiaryId"] = beneficiary_id
    payload["Referral"]["projectBeneficiaryClientReferenceId"] = str(uuid.uuid4())
    payload["Referral"]["sideEffectId"] = side_effect_id
    payload["Referral"]["sideEffectClientReferenceId"] = str(uuid.uuid4())
    payload["Referral"]["recipientType"] = "FACILITY"
    payload["Referral"]["recipientId"] = str(uuid.uuid4())
    payload["Referral"]["reasons"] = ["FEVER", "VOMITING"]

    url = f"/{project}/referralmanagement/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_create_hf_referral_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    project_id = extract_id_from_file("Project ID:")
    project_facility_id = extract_id_from_file("Project Facility ID:")

    assert project_id, "Project ID not found in file"
    assert project_facility_id, "Project Facility ID not found in file"

    payload = load_payload("referralmanagement/hf_referral", "create_hf_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HFReferral"]["tenantId"] = "invalid.tenant.id"
    payload["HFReferral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["HFReferral"]["projectId"] = project_id
    payload["HFReferral"]["projectFacilityId"] = project_facility_id
    payload["HFReferral"]["symptom"] = "fever"
    payload["HFReferral"]["symptomSurveyId"] = str(uuid.uuid4())

    url = f"/referralmanagement/hf-referral/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [401], f"Expected error status code, got: {response.status_code}"
    print(f"Request correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_side_effect_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    side_effect_id = extract_id_from_file("Side Effect ID:")
    if not side_effect_id:
        # Create side effect with all dependencies if not found
        variant_response = create_product_variant(token, client)
        assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
        variant_id = variant_response.json()["ProductVariant"][0]["id"]
        project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        create_project_resource(token, client, project_id, variant_id)
        household_id, household_client_ref_id, _ = create_household(token, client)
        individual_id, individual_client_ref_id, _, _ = create_individual(token, client)
        create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
        beneficiary_id, beneficiary_client_ref_id, _ = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
        task_id, task_client_ref_id, _ = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
        side_effect_id, _, _ = create_side_effect(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)

    payload = load_payload("referralmanagement/side_effect", "search_side_effect.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SideEffect"]["id"] = [side_effect_id]

    url = f"/referralmanagement/side-effect/v1/_search?tenantId=invalid.tenant.id"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_referral_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    referral_id = extract_id_from_file("Referral ID:")
    if not referral_id:
        # Create referral with all dependencies if not found
        variant_response = create_product_variant(token, client)
        assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
        variant_id = variant_response.json()["ProductVariant"][0]["id"]
        project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        create_project_resource(token, client, project_id, variant_id)
        facility_response = create_facility(token, client)
        assert facility_response.status_code in [200, 202], f"Facility creation failed"
        facility_id = facility_response.json()["Facility"]["id"]
        create_project_facility(token, client, project_id, facility_id)
        household_id, household_client_ref_id, _ = create_household(token, client)
        individual_id, individual_client_ref_id, _, _ = create_individual(token, client)
        create_household_member(token, client, household_id, household_client_ref_id, individual_id, individual_client_ref_id)
        beneficiary_id, beneficiary_client_ref_id, _ = create_project_beneficiary(token, client, project_id, individual_id, individual_client_ref_id)
        task_id, task_client_ref_id, _ = create_project_task(token, client, project_id, beneficiary_id, beneficiary_client_ref_id, variant_id)
        side_effect_id, side_effect_client_ref_id, _ = create_side_effect(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)
        referral_id, _ = create_referral(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id, side_effect_id, side_effect_client_ref_id, facility_id)

    payload = load_payload("referralmanagement/referral", "search_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Referral"]["id"] = [referral_id]

    url = f"/referralmanagement/v1/_search?tenantId=invalid.tenant.id"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_hf_referral_with_invalid_tenant_id():
    token = get_auth_token("user")
    client = APIClient(token=token)

    hf_referral_id = extract_id_from_file("HF Referral ID:")
    if not hf_referral_id:
        # Create HF referral with all dependencies if not found
        variant_response = create_product_variant(token, client)
        assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
        variant_id = variant_response.json()["ProductVariant"][0]["id"]
        project_id, _ = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
        facility_response = create_facility(token, client)
        assert facility_response.status_code in [200, 202], f"Facility creation failed"
        facility_id = facility_response.json()["Facility"]["id"]
        project_facility_id, _ = create_project_facility(token, client, project_id, facility_id)
        hf_referral_id, _ = create_hf_referral(token, client, project_id, project_facility_id)

    payload = load_payload("referralmanagement/hf_referral", "search_hf_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HFReferral"]["id"] = [hf_referral_id]

    url = f"/referralmanagement/hf-referral/v1/_search?tenantId=invalid.tenant.id"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.positive
def test_update_side_effect():
    """Test to update a side effect. Creates all dependencies internally first, then updates symptoms."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed"

    print("Creating project resource...")
    _, resource_status = create_project_resource(token, client, project_id, variant_id)
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
    assert task_status in [200, 202], f"Project Task creation failed"

    print("Creating side effect...")
    side_effect_data, side_effect_status = create_side_effect_full(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)
    assert side_effect_status in [200, 202], f"Side Effect creation failed"
    print(f"Side Effect created with ID: {side_effect_data['id']}")

    # Step 2: Use create response data directly (async APIs may not be immediately searchable)
    original_symptoms = side_effect_data.get("symptoms", [])
    print(f"Original symptoms: {original_symptoms}")

    # Step 3: Update the side effect (change symptoms)
    new_symptoms = ["HEADACHE", "NAUSEA", "DIZZINESS"]
    response = update_side_effect(token, client, side_effect_data, new_symptoms)
    assert response.status_code in [200, 202], f"Side Effect update failed: {response.text}"

    # Step 4: Verify update
    updated_side_effect = response.json()["SideEffect"]
    assert updated_side_effect["symptoms"] == new_symptoms, f"Symptoms not updated. Expected {new_symptoms}, got {updated_side_effect.get('symptoms')}"
    print(f"Side Effect updated successfully. Symptoms changed from {original_symptoms} to {new_symptoms}")


@pytest.mark.positive
def test_update_referral():
    """Test to update a referral. Creates all dependencies internally first, then updates reasons."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed"

    print("Creating project resource...")
    _, resource_status = create_project_resource(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed"

    print("Creating facility...")
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed"
    facility_id = facility_response.json()["Facility"]["id"]

    print("Creating project facility...")
    _, project_facility_status = create_project_facility(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility mapping failed"

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
    assert task_status in [200, 202], f"Project Task creation failed"

    print("Creating side effect...")
    side_effect_id, side_effect_client_ref_id, side_effect_status = create_side_effect(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)
    assert side_effect_status in [200, 202], f"Side Effect creation failed"

    print("Creating referral...")
    referral_data, referral_status = create_referral_full(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id, side_effect_id, side_effect_client_ref_id, facility_id)
    assert referral_status in [200, 202], f"Referral creation failed"
    print(f"Referral created with ID: {referral_data['id']}")

    # Step 2: Use create response data directly (async APIs may not be immediately searchable)
    original_reasons = referral_data.get("reasons", [])
    print(f"Original reasons: {original_reasons}")

    # Step 3: Update the referral (change reasons)
    new_reasons = ["VOMITING", "DIARRHEA"]
    response = update_referral(token, client, referral_data, new_reasons)
    assert response.status_code in [200, 202], f"Referral update failed: {response.text}"

    # Step 4: Verify update
    updated_referral = response.json()["Referral"]
    assert updated_referral["reasons"] == new_reasons, f"Reasons not updated. Expected {new_reasons}, got {updated_referral.get('reasons')}"
    print(f"Referral updated successfully. Reasons changed from {original_reasons} to {new_reasons}")


@pytest.mark.positive
def test_update_hf_referral():
    """Test to update an HF referral. Creates all dependencies internally first, then updates symptom."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed"
    print(f"Project created with ID: {project_id}")

    print("Creating facility...")
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed"
    facility_id = facility_response.json()["Facility"]["id"]

    print("Creating project facility...")
    project_facility_id, project_facility_status = create_project_facility(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility mapping failed"

    print("Creating HF referral...")
    hf_referral_data, hf_referral_status = create_hf_referral_full(token, client, project_id, project_facility_id)
    assert hf_referral_status in [200, 202], f"HF Referral creation failed"
    print(f"HF Referral created with ID: {hf_referral_data['id']}")

    # Step 2: Use create response data directly (async APIs may not be immediately searchable)
    original_symptom = hf_referral_data.get("symptom", "")
    print(f"Original symptom: {original_symptom}")

    # Step 3: Update the HF referral (change symptom)
    new_symptom = "malaria"
    response = update_hf_referral(token, client, hf_referral_data, new_symptom)
    assert response.status_code in [200, 202], f"HF Referral update failed: {response.text}"

    # Step 4: Verify update
    updated_hf_referral = response.json()["HFReferral"]
    assert updated_hf_referral["symptom"] == new_symptom, f"Symptom not updated. Expected {new_symptom}, got {updated_hf_referral.get('symptom')}"
    print(f"HF Referral updated successfully. Symptom changed from '{original_symptom}' to '{new_symptom}'")


@pytest.mark.positive
def test_delete_side_effect():
    """Test to delete a side effect. Creates all dependencies internally first, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed"

    print("Creating project resource...")
    _, resource_status = create_project_resource(token, client, project_id, variant_id)
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
    assert task_status in [200, 202], f"Project Task creation failed"

    print("Creating side effect...")
    side_effect_data, side_effect_status = create_side_effect_full(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)
    assert side_effect_status in [200, 202], f"Side Effect creation failed"
    side_effect_id = side_effect_data['id']
    print(f"Side Effect created with ID: {side_effect_id}")

    # Step 2: Delete the side effect
    print("Deleting side effect...")
    response = delete_side_effect(token, client, side_effect_data)
    assert response.status_code in [200, 202], f"Side Effect delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_side_effect = response.json()["SideEffect"]
    assert deleted_side_effect["isDeleted"] == True, f"Side Effect not marked as deleted"
    print(f"Side Effect {side_effect_id} deleted successfully")


@pytest.mark.positive
def test_delete_referral():
    """Test to delete a referral. Creates all dependencies internally first, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed"

    print("Creating project resource...")
    _, resource_status = create_project_resource(token, client, project_id, variant_id)
    assert resource_status in [200, 202], f"Project Resource creation failed"

    print("Creating facility...")
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed"
    facility_id = facility_response.json()["Facility"]["id"]

    print("Creating project facility...")
    _, project_facility_status = create_project_facility(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility mapping failed"

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
    assert task_status in [200, 202], f"Project Task creation failed"

    print("Creating side effect...")
    side_effect_id, side_effect_client_ref_id, side_effect_status = create_side_effect(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id)
    assert side_effect_status in [200, 202], f"Side Effect creation failed"

    print("Creating referral...")
    referral_data, referral_status = create_referral_full(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id, side_effect_id, side_effect_client_ref_id, facility_id)
    assert referral_status in [200, 202], f"Referral creation failed"
    referral_id = referral_data['id']
    print(f"Referral created with ID: {referral_id}")

    # Step 2: Delete the referral
    print("Deleting referral...")
    response = delete_referral(token, client, referral_data)
    assert response.status_code in [200, 202], f"Referral delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_referral = response.json()["Referral"]
    assert deleted_referral["isDeleted"] == True, f"Referral not marked as deleted"
    print(f"Referral {referral_id} deleted successfully")


@pytest.mark.positive
def test_delete_hf_referral():
    """Test to delete an HF referral. Creates all dependencies internally first, then deletes it."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Creating product variant...")
    variant_response = create_product_variant(token, client)
    assert variant_response.status_code in [200, 202], f"Product Variant creation failed"
    variant_id = variant_response.json()["ProductVariant"][0]["id"]

    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id, variant_id)
    assert project_status in [200, 202], f"Project creation failed"
    print(f"Project created with ID: {project_id}")

    print("Creating facility...")
    facility_response = create_facility(token, client)
    assert facility_response.status_code in [200, 202], f"Facility creation failed"
    facility_id = facility_response.json()["Facility"]["id"]

    print("Creating project facility...")
    project_facility_id, project_facility_status = create_project_facility(token, client, project_id, facility_id)
    assert project_facility_status in [200, 202], f"Project Facility mapping failed"

    print("Creating HF referral...")
    hf_referral_data, hf_referral_status = create_hf_referral_full(token, client, project_id, project_facility_id)
    assert hf_referral_status in [200, 202], f"HF Referral creation failed"
    hf_referral_id = hf_referral_data['id']
    print(f"HF Referral created with ID: {hf_referral_id}")

    # Step 2: Delete the HF referral
    print("Deleting HF referral...")
    response = delete_hf_referral(token, client, hf_referral_data)
    assert response.status_code in [200, 202], f"HF Referral delete failed: {response.text}"

    # Step 3: Verify deletion
    deleted_hf_referral = response.json()["HFReferral"]
    assert deleted_hf_referral["isDeleted"] == True, f"HF Referral not marked as deleted"
    print(f"HF Referral {hf_referral_id} deleted successfully")


# --- Helper functions ---

def create_side_effect(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id):
    payload = load_payload("referralmanagement/side_effect", "create_side_effect.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SideEffect"]["tenantId"] = tenantId
    payload["SideEffect"]["clientReferenceId"] = str(uuid.uuid4())
    payload["SideEffect"]["taskId"] = task_id
    payload["SideEffect"]["taskClientReferenceId"] = task_client_ref_id
    payload["SideEffect"]["projectBeneficiaryId"] = beneficiary_id
    payload["SideEffect"]["projectBeneficiaryClientReferenceId"] = beneficiary_client_ref_id
    payload["SideEffect"]["symptoms"] = ["FEVER", "VOMITING"]

    url = f"/referralmanagement/side-effect/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Side Effect creation failed with status {response.status_code}: {response.text}")

    side_effect_data = response.json()["SideEffect"]
    return side_effect_data["id"], side_effect_data["clientReferenceId"], response.status_code


def create_referral(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id, side_effect_id, side_effect_client_ref_id, facility_id):
    payload = load_payload("referralmanagement/referral", "create_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Referral"]["tenantId"] = tenantId
    payload["Referral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Referral"]["taskId"] = task_id
    payload["Referral"]["taskClientReferenceId"] = task_client_ref_id
    payload["Referral"]["projectBeneficiaryId"] = beneficiary_id
    payload["Referral"]["projectBeneficiaryClientReferenceId"] = beneficiary_client_ref_id
    payload["Referral"]["sideEffectId"] = side_effect_id
    payload["Referral"]["sideEffectClientReferenceId"] = side_effect_client_ref_id
    payload["Referral"]["recipientType"] = "FACILITY"
    payload["Referral"]["recipientId"] = facility_id
    payload["Referral"]["reasons"] = ["FEVER"]

    url = f"/referralmanagement/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Referral creation failed with status {response.status_code}: {response.text}")

    referral_data = response.json()["Referral"]
    return referral_data["id"], response.status_code


def create_hf_referral(token, client, project_id, project_facility_id):
    payload = load_payload("referralmanagement/hf_referral", "create_hf_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HFReferral"]["tenantId"] = tenantId
    payload["HFReferral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["HFReferral"]["projectId"] = project_id
    payload["HFReferral"]["projectFacilityId"] = project_facility_id
    payload["HFReferral"]["symptom"] = "fever"
    payload["HFReferral"]["symptomSurveyId"] = str(uuid.uuid4())

    url = f"/referralmanagement/hf-referral/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"HF Referral creation failed with status {response.status_code}: {response.text}")

    hf_referral_data = response.json()["HFReferral"]
    return hf_referral_data["id"], response.status_code


def search_hf_referral_all(token, client):
    """Search for all HF referrals without any filter."""
    payload = load_payload("referralmanagement/hf_referral", "search_hf_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HFReferral"] = {}  # Empty filter to get all

    url = f"/referralmanagement/hf-referral/v1/_search?limit=10&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"HF Referral search failed with status {response.status_code}: {response.text}")

    return response.json().get("HFReferrals", [])


def search_side_effect_all(token, client):
    """Search for all side effects without any filter."""
    payload = load_payload("referralmanagement/side_effect", "search_side_effect.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SideEffect"] = {}  # Empty filter to get all

    url = f"/referralmanagement/side-effect/v1/_search?limit=10&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Side Effect search failed with status {response.status_code}: {response.text}")

    return response.json().get("SideEffects", [])


def search_referral_all(token, client):
    """Search for all referrals without any filter."""
    payload = load_payload("referralmanagement/referral", "search_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Referral"] = {}  # Empty filter to get all

    url = f"/referralmanagement/v1/_search?limit=10&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Referral search failed with status {response.status_code}: {response.text}")

    return response.json().get("Referrals", [])


def search_side_effect_by_id(token, client, side_effect_id):
    """Search for a side effect by ID and return full data."""
    payload = load_payload("referralmanagement/side_effect", "search_side_effect.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SideEffect"]["id"] = [side_effect_id]

    url = f"/referralmanagement/side-effect/v1/_search?limit=100&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Side Effect search failed with status {response.status_code}: {response.text}")

    return response.json().get("SideEffects", [])


def search_referral_by_id(token, client, referral_id):
    """Search for a referral by ID and return full data."""
    payload = load_payload("referralmanagement/referral", "search_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Referral"]["id"] = [referral_id]

    url = f"/referralmanagement/v1/_search?limit=100&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Referral search failed with status {response.status_code}: {response.text}")

    return response.json().get("Referrals", [])


def search_hf_referral_by_id(token, client, hf_referral_id):
    """Search for an HF referral by ID and return full data."""
    payload = load_payload("referralmanagement/hf_referral", "search_hf_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HFReferral"]["id"] = [hf_referral_id]

    url = f"/referralmanagement/hf-referral/v1/_search?limit=100&offset=0&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"HF Referral search failed with status {response.status_code}: {response.text}")

    return response.json().get("HFReferrals", [])


def create_referral_with_client_ref(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id, side_effect_id, side_effect_client_ref_id, facility_id):
    """Create a referral and return id, clientReferenceId, and status_code."""
    payload = load_payload("referralmanagement/referral", "create_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Referral"]["tenantId"] = tenantId
    payload["Referral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Referral"]["taskId"] = task_id
    payload["Referral"]["taskClientReferenceId"] = task_client_ref_id
    payload["Referral"]["projectBeneficiaryId"] = beneficiary_id
    payload["Referral"]["projectBeneficiaryClientReferenceId"] = beneficiary_client_ref_id
    payload["Referral"]["sideEffectId"] = side_effect_id
    payload["Referral"]["sideEffectClientReferenceId"] = side_effect_client_ref_id
    payload["Referral"]["recipientType"] = "FACILITY"
    payload["Referral"]["recipientId"] = facility_id
    payload["Referral"]["reasons"] = ["FEVER"]

    url = f"/referralmanagement/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Referral creation failed with status {response.status_code}: {response.text}")

    referral_data = response.json()["Referral"]
    return referral_data["id"], referral_data["clientReferenceId"], response.status_code


def create_hf_referral_with_client_ref(token, client, project_id, project_facility_id):
    """Create an HF referral and return id, clientReferenceId, and status_code."""
    payload = load_payload("referralmanagement/hf_referral", "create_hf_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HFReferral"]["tenantId"] = tenantId
    payload["HFReferral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["HFReferral"]["projectId"] = project_id
    payload["HFReferral"]["projectFacilityId"] = project_facility_id
    payload["HFReferral"]["symptom"] = "fever"
    payload["HFReferral"]["symptomSurveyId"] = str(uuid.uuid4())

    url = f"/referralmanagement/hf-referral/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"HF Referral creation failed with status {response.status_code}: {response.text}")

    hf_referral_data = response.json()["HFReferral"]
    return hf_referral_data["id"], hf_referral_data["clientReferenceId"], response.status_code


def create_side_effect_full(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id):
    """Create a side effect and return full data and status_code for update operations."""
    payload = load_payload("referralmanagement/side_effect", "create_side_effect.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["SideEffect"]["tenantId"] = tenantId
    payload["SideEffect"]["clientReferenceId"] = str(uuid.uuid4())
    payload["SideEffect"]["taskId"] = task_id
    payload["SideEffect"]["taskClientReferenceId"] = task_client_ref_id
    payload["SideEffect"]["projectBeneficiaryId"] = beneficiary_id
    payload["SideEffect"]["projectBeneficiaryClientReferenceId"] = beneficiary_client_ref_id
    payload["SideEffect"]["symptoms"] = ["FEVER", "VOMITING"]

    url = f"/referralmanagement/side-effect/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Side Effect creation failed with status {response.status_code}: {response.text}")

    return response.json()["SideEffect"], response.status_code


def create_referral_full(token, client, task_id, task_client_ref_id, beneficiary_id, beneficiary_client_ref_id, side_effect_id, side_effect_client_ref_id, facility_id):
    """Create a referral and return full data and status_code for update operations."""
    payload = load_payload("referralmanagement/referral", "create_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Referral"]["tenantId"] = tenantId
    payload["Referral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Referral"]["taskId"] = task_id
    payload["Referral"]["taskClientReferenceId"] = task_client_ref_id
    payload["Referral"]["projectBeneficiaryId"] = beneficiary_id
    payload["Referral"]["projectBeneficiaryClientReferenceId"] = beneficiary_client_ref_id
    payload["Referral"]["sideEffectId"] = side_effect_id
    payload["Referral"]["sideEffectClientReferenceId"] = side_effect_client_ref_id
    payload["Referral"]["recipientType"] = "FACILITY"
    payload["Referral"]["recipientId"] = facility_id
    payload["Referral"]["reasons"] = ["FEVER"]

    url = f"/referralmanagement/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Referral creation failed with status {response.status_code}: {response.text}")

    return response.json()["Referral"], response.status_code


def create_hf_referral_full(token, client, project_id, project_facility_id):
    """Create an HF referral and return full data and status_code for update operations."""
    payload = load_payload("referralmanagement/hf_referral", "create_hf_referral.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["HFReferral"]["tenantId"] = tenantId
    payload["HFReferral"]["clientReferenceId"] = str(uuid.uuid4())
    payload["HFReferral"]["projectId"] = project_id
    payload["HFReferral"]["projectFacilityId"] = project_facility_id
    payload["HFReferral"]["symptom"] = "fever"
    payload["HFReferral"]["symptomSurveyId"] = str(uuid.uuid4())

    url = f"/referralmanagement/hf-referral/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"HF Referral creation failed with status {response.status_code}: {response.text}")

    return response.json()["HFReferral"], response.status_code


def update_side_effect(token, client, side_effect_data, new_symptoms):
    """
    Update a side effect's symptoms.

    Args:
        side_effect_data: Full side effect object from search
        new_symptoms: New symptoms list to set
    """
    payload = load_payload("referralmanagement/side_effect", "update_side_effect.json")

    # Copy required fields from the searched side effect
    payload["SideEffect"]["id"] = side_effect_data["id"]
    payload["SideEffect"]["tenantId"] = side_effect_data["tenantId"]
    payload["SideEffect"]["clientReferenceId"] = side_effect_data["clientReferenceId"]
    payload["SideEffect"]["rowVersion"] = side_effect_data["rowVersion"]
    payload["SideEffect"]["auditDetails"] = side_effect_data["auditDetails"]
    payload["SideEffect"]["clientAuditDetails"] = side_effect_data.get("clientAuditDetails")
    payload["SideEffect"]["taskId"] = side_effect_data["taskId"]
    payload["SideEffect"]["taskClientReferenceId"] = side_effect_data.get("taskClientReferenceId")
    payload["SideEffect"]["projectBeneficiaryId"] = side_effect_data["projectBeneficiaryId"]
    payload["SideEffect"]["projectBeneficiaryClientReferenceId"] = side_effect_data.get("projectBeneficiaryClientReferenceId")
    payload["SideEffect"]["symptoms"] = new_symptoms
    payload["RequestInfo"] = get_request_info(token)

    url = f"/referralmanagement/side-effect/v1/_update"
    response = client.post(url, payload)
    return response


def update_referral(token, client, referral_data, new_reasons):
    """
    Update a referral's reasons.

    Args:
        referral_data: Full referral object from search
        new_reasons: New reasons list to set
    """
    payload = load_payload("referralmanagement/referral", "update_referral.json")

    # Copy required fields from the searched referral
    payload["Referral"]["id"] = referral_data["id"]
    payload["Referral"]["tenantId"] = referral_data["tenantId"]
    payload["Referral"]["clientReferenceId"] = referral_data["clientReferenceId"]
    payload["Referral"]["rowVersion"] = referral_data["rowVersion"]
    payload["Referral"]["auditDetails"] = referral_data["auditDetails"]
    payload["Referral"]["clientAuditDetails"] = referral_data.get("clientAuditDetails")
    payload["Referral"]["projectBeneficiaryId"] = referral_data["projectBeneficiaryId"]
    payload["Referral"]["projectBeneficiaryClientReferenceId"] = referral_data.get("projectBeneficiaryClientReferenceId")
    payload["Referral"]["recipientType"] = referral_data.get("recipientType")
    payload["Referral"]["recipientId"] = referral_data.get("recipientId")
    payload["Referral"]["reasons"] = new_reasons
    payload["RequestInfo"] = get_request_info(token)

    url = f"/referralmanagement/v1/_update"
    response = client.post(url, payload)
    return response


def update_hf_referral(token, client, hf_referral_data, new_symptom):
    """
    Update an HF referral's symptom.

    Args:
        hf_referral_data: Full HF referral object from search
        new_symptom: New symptom value to set
    """
    payload = load_payload("referralmanagement/hf_referral", "update_hf_referral.json")

    # Copy required fields from the searched HF referral
    payload["HFReferral"]["id"] = hf_referral_data["id"]
    payload["HFReferral"]["tenantId"] = hf_referral_data["tenantId"]
    payload["HFReferral"]["clientReferenceId"] = hf_referral_data["clientReferenceId"]
    payload["HFReferral"]["rowVersion"] = hf_referral_data["rowVersion"]
    payload["HFReferral"]["auditDetails"] = hf_referral_data["auditDetails"]
    payload["HFReferral"]["clientAuditDetails"] = hf_referral_data.get("clientAuditDetails")
    payload["HFReferral"]["projectId"] = hf_referral_data["projectId"]
    payload["HFReferral"]["projectFacilityId"] = hf_referral_data.get("projectFacilityId")
    payload["HFReferral"]["symptom"] = new_symptom
    payload["HFReferral"]["symptomSurveyId"] = hf_referral_data.get("symptomSurveyId")
    payload["RequestInfo"] = get_request_info(token)

    url = f"/referralmanagement/hf-referral/v1/_update"
    response = client.post(url, payload)
    return response


def delete_side_effect(token, client, side_effect_data):
    """
    Delete a side effect (soft delete by setting isDeleted=true).

    Args:
        side_effect_data: Full side effect object from create response
    """
    payload = load_payload("referralmanagement/side_effect", "delete_side_effect.json")

    # Copy required fields from the created side effect
    payload["SideEffect"]["id"] = side_effect_data["id"]
    payload["SideEffect"]["tenantId"] = side_effect_data["tenantId"]
    payload["SideEffect"]["clientReferenceId"] = side_effect_data["clientReferenceId"]
    payload["SideEffect"]["rowVersion"] = side_effect_data["rowVersion"]
    payload["SideEffect"]["auditDetails"] = side_effect_data["auditDetails"]
    payload["SideEffect"]["clientAuditDetails"] = side_effect_data.get("clientAuditDetails")
    payload["SideEffect"]["taskId"] = side_effect_data["taskId"]
    payload["SideEffect"]["taskClientReferenceId"] = side_effect_data.get("taskClientReferenceId")
    payload["SideEffect"]["projectBeneficiaryId"] = side_effect_data["projectBeneficiaryId"]
    payload["SideEffect"]["projectBeneficiaryClientReferenceId"] = side_effect_data.get("projectBeneficiaryClientReferenceId")
    payload["SideEffect"]["symptoms"] = side_effect_data.get("symptoms", [])
    payload["SideEffect"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/referralmanagement/side-effect/v1/_delete"
    response = client.post(url, payload)
    return response


def delete_referral(token, client, referral_data):
    """
    Delete a referral (soft delete by setting isDeleted=true).

    Args:
        referral_data: Full referral object from create response
    """
    payload = load_payload("referralmanagement/referral", "delete_referral.json")

    # Copy required fields from the created referral
    payload["Referral"]["id"] = referral_data["id"]
    payload["Referral"]["tenantId"] = referral_data["tenantId"]
    payload["Referral"]["clientReferenceId"] = referral_data["clientReferenceId"]
    payload["Referral"]["rowVersion"] = referral_data["rowVersion"]
    payload["Referral"]["auditDetails"] = referral_data["auditDetails"]
    payload["Referral"]["clientAuditDetails"] = referral_data.get("clientAuditDetails")
    payload["Referral"]["projectBeneficiaryId"] = referral_data["projectBeneficiaryId"]
    payload["Referral"]["projectBeneficiaryClientReferenceId"] = referral_data.get("projectBeneficiaryClientReferenceId")
    payload["Referral"]["recipientType"] = referral_data.get("recipientType")
    payload["Referral"]["recipientId"] = referral_data.get("recipientId")
    payload["Referral"]["reasons"] = referral_data.get("reasons", [])
    payload["Referral"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/referralmanagement/v1/_delete"
    response = client.post(url, payload)
    return response


def delete_hf_referral(token, client, hf_referral_data):
    """
    Delete an HF referral (soft delete by setting isDeleted=true).

    Args:
        hf_referral_data: Full HF referral object from create response
    """
    payload = load_payload("referralmanagement/hf_referral", "delete_hf_referral.json")

    # Copy required fields from the created HF referral
    payload["HFReferral"]["id"] = hf_referral_data["id"]
    payload["HFReferral"]["tenantId"] = hf_referral_data["tenantId"]
    payload["HFReferral"]["clientReferenceId"] = hf_referral_data["clientReferenceId"]
    payload["HFReferral"]["rowVersion"] = hf_referral_data["rowVersion"]
    payload["HFReferral"]["auditDetails"] = hf_referral_data["auditDetails"]
    payload["HFReferral"]["clientAuditDetails"] = hf_referral_data.get("clientAuditDetails")
    payload["HFReferral"]["projectId"] = hf_referral_data["projectId"]
    payload["HFReferral"]["projectFacilityId"] = hf_referral_data.get("projectFacilityId")
    payload["HFReferral"]["symptom"] = hf_referral_data.get("symptom")
    payload["HFReferral"]["symptomSurveyId"] = hf_referral_data.get("symptomSurveyId")
    payload["HFReferral"]["isDeleted"] = True
    payload["RequestInfo"] = get_request_info(token)

    url = f"/referralmanagement/hf-referral/v1/_delete"
    response = client.post(url, payload)
    return response
