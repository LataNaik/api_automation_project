import uuid
import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import extract_id_from_file
from utils.config import tenantId, boundaryType, boundaryCode, search_limit, search_offset, invalidTenantId
from tests.test_project_service import create_individual_project, create_project_resource, create_project_facility, create_project_staff
from tests.test_product_service import create_product_variant
from tests.test_facility_service import create_facility
from tests.test_hrms_service import create_employee


# Stock service name is same across all environments
STOCK_SERVICE = "stock"


# --- Test functions ---

@pytest.mark.positive
def test_create_stock_received_between_facilities():
    """
    Test to create a stock RECEIVED transaction between two facilities.
    Internally creates: project, product variants, project resources, facilities
    Then uses those details for stock creation with transaction type RECEIVED.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup all prerequisites
    prerequisites = setup_stock_prerequisites(token, client)

    # Create stock RECEIVED transaction
    print("Creating stock RECEIVED transaction...")
    stock_id, stock_client_ref_id, stock_status = create_stock(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_facility_id=prerequisites["sender_facility_id"],
        receiver_facility_id=prerequisites["receiver_facility_id"],
        transaction_type="RECEIVED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock RECEIVED transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock RECEIVED Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: RECEIVED\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")
        f.write(f"Sender Facility ID: {prerequisites['sender_facility_id']}\n")
        f.write(f"Receiver Facility ID: {prerequisites['receiver_facility_id']}\n")


@pytest.mark.positive
def test_create_stock_dispatched_between_facilities():
    """
    Test to create a stock DISPATCHED transaction between two facilities.
    Internally creates: project, product variants, project resources, facilities
    Then uses those details for stock creation with transaction type DISPATCHED.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup all prerequisites
    prerequisites = setup_stock_prerequisites(token, client)

    # Create stock DISPATCHED transaction
    print("Creating stock DISPATCHED transaction...")
    stock_id, stock_client_ref_id, stock_status = create_stock(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_facility_id=prerequisites["sender_facility_id"],
        receiver_facility_id=prerequisites["receiver_facility_id"],
        transaction_type="DISPATCHED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock DISPATCHED transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock DISPATCHED Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: DISPATCHED\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")
        f.write(f"Sender Facility ID: {prerequisites['sender_facility_id']}\n")
        f.write(f"Receiver Facility ID: {prerequisites['receiver_facility_id']}\n")


@pytest.mark.positive
def test_create_stock_received_from_staff_to_warehouse():
    """
    Test to create a stock RECEIVED transaction from STAFF to WAREHOUSE.
    Internally creates: employee, project staff, facility, project, product variants, project resources
    Then uses staff UUID as sender and facility as receiver.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup prerequisites with staff
    prerequisites = setup_stock_prerequisites_with_staff(token, client)

    # Create stock RECEIVED transaction from STAFF to WAREHOUSE
    print("Creating stock RECEIVED transaction from STAFF to WAREHOUSE...")
    stock_id, stock_client_ref_id, stock_status = create_stock_with_sender_receiver_types(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_id=prerequisites["staff_user_uuid"],
        sender_type="STAFF",
        receiver_id=prerequisites["receiver_facility_id"],
        receiver_type="WAREHOUSE",
        transaction_type="RECEIVED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock RECEIVED (STAFF to WAREHOUSE) transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock RECEIVED (STAFF to WAREHOUSE) Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: RECEIVED\n")
        f.write(f"Sender Type: STAFF\n")
        f.write(f"Sender ID (Staff UUID): {prerequisites['staff_user_uuid']}\n")
        f.write(f"Receiver Type: WAREHOUSE\n")
        f.write(f"Receiver Facility ID: {prerequisites['receiver_facility_id']}\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")


@pytest.mark.positive
def test_create_stock_dispatched_from_staff_to_warehouse():
    """
    Test to create a stock DISPATCHED transaction from STAFF to WAREHOUSE.
    Internally creates: employee, project staff, facility, project, product variants, project resources
    Then uses staff UUID as sender and facility as receiver.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup prerequisites with staff
    prerequisites = setup_stock_prerequisites_with_staff(token, client)

    # Create stock DISPATCHED transaction from STAFF to WAREHOUSE
    print("Creating stock DISPATCHED transaction from STAFF to WAREHOUSE...")
    stock_id, stock_client_ref_id, stock_status = create_stock_with_sender_receiver_types(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_id=prerequisites["staff_user_uuid"],
        sender_type="STAFF",
        receiver_id=prerequisites["receiver_facility_id"],
        receiver_type="WAREHOUSE",
        transaction_type="DISPATCHED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock DISPATCHED (STAFF to WAREHOUSE) transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock DISPATCHED (STAFF to WAREHOUSE) Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: DISPATCHED\n")
        f.write(f"Sender Type: STAFF\n")
        f.write(f"Sender ID (Staff UUID): {prerequisites['staff_user_uuid']}\n")
        f.write(f"Receiver Type: WAREHOUSE\n")
        f.write(f"Receiver Facility ID: {prerequisites['receiver_facility_id']}\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")


@pytest.mark.positive
def test_create_stock_received_from_warehouse_to_staff():
    """
    Test to create a stock RECEIVED transaction from WAREHOUSE to STAFF.
    Internally creates: employee, project staff, facility, project, product variants, project resources
    Then uses facility as sender and staff UUID as receiver.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup prerequisites with staff
    prerequisites = setup_stock_prerequisites_with_staff(token, client)

    # Create stock RECEIVED transaction from WAREHOUSE to STAFF
    print("Creating stock RECEIVED transaction from WAREHOUSE to STAFF...")
    stock_id, stock_client_ref_id, stock_status = create_stock_with_sender_receiver_types(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_id=prerequisites["receiver_facility_id"],
        sender_type="WAREHOUSE",
        receiver_id=prerequisites["staff_user_uuid"],
        receiver_type="STAFF",
        transaction_type="RECEIVED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock RECEIVED (WAREHOUSE to STAFF) transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock RECEIVED (WAREHOUSE to STAFF) Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: RECEIVED\n")
        f.write(f"Sender Type: WAREHOUSE\n")
        f.write(f"Sender Facility ID: {prerequisites['receiver_facility_id']}\n")
        f.write(f"Receiver Type: STAFF\n")
        f.write(f"Receiver ID (Staff UUID): {prerequisites['staff_user_uuid']}\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")


@pytest.mark.positive
def test_create_stock_dispatched_from_warehouse_to_staff():
    """
    Test to create a stock DISPATCHED transaction from WAREHOUSE to STAFF.
    Internally creates: employee, project staff, facility, project, product variants, project resources
    Then uses facility as sender and staff UUID as receiver.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup prerequisites with staff
    prerequisites = setup_stock_prerequisites_with_staff(token, client)

    # Create stock DISPATCHED transaction from WAREHOUSE to STAFF
    print("Creating stock DISPATCHED transaction from WAREHOUSE to STAFF...")
    stock_id, stock_client_ref_id, stock_status = create_stock_with_sender_receiver_types(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_id=prerequisites["receiver_facility_id"],
        sender_type="WAREHOUSE",
        receiver_id=prerequisites["staff_user_uuid"],
        receiver_type="STAFF",
        transaction_type="DISPATCHED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock DISPATCHED (WAREHOUSE to STAFF) transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock DISPATCHED (WAREHOUSE to STAFF) Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: DISPATCHED\n")
        f.write(f"Sender Type: WAREHOUSE\n")
        f.write(f"Sender Facility ID: {prerequisites['receiver_facility_id']}\n")
        f.write(f"Receiver Type: STAFF\n")
        f.write(f"Receiver ID (Staff UUID): {prerequisites['staff_user_uuid']}\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")


@pytest.mark.positive
def test_create_stock_received_between_staff():
    """
    Test to create a stock RECEIVED transaction between two STAFF members.
    Internally creates: two employees, two project staff, project, product variants, project resources
    Then uses staff1 UUID as sender and staff2 UUID as receiver.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup prerequisites with two staff members
    prerequisites = setup_stock_prerequisites_with_two_staff(token, client)

    # Create stock RECEIVED transaction between two STAFF
    print("Creating stock RECEIVED transaction between two STAFF...")
    stock_id, stock_client_ref_id, stock_status = create_stock_with_sender_receiver_types(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_id=prerequisites["staff_1_user_uuid"],
        sender_type="STAFF",
        receiver_id=prerequisites["staff_2_user_uuid"],
        receiver_type="STAFF",
        transaction_type="RECEIVED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock RECEIVED (STAFF to STAFF) transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock RECEIVED (STAFF to STAFF) Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: RECEIVED\n")
        f.write(f"Sender Type: STAFF\n")
        f.write(f"Sender ID (Staff 1 UUID): {prerequisites['staff_1_user_uuid']}\n")
        f.write(f"Receiver Type: STAFF\n")
        f.write(f"Receiver ID (Staff 2 UUID): {prerequisites['staff_2_user_uuid']}\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")


@pytest.mark.positive
def test_create_stock_dispatched_between_staff():
    """
    Test to create a stock DISPATCHED transaction between two STAFF members.
    Internally creates: two employees, two project staff, project, product variants, project resources
    Then uses staff1 UUID as sender and staff2 UUID as receiver.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup prerequisites with two staff members
    prerequisites = setup_stock_prerequisites_with_two_staff(token, client)

    # Create stock DISPATCHED transaction between two STAFF
    print("Creating stock DISPATCHED transaction between two STAFF...")
    stock_id, stock_client_ref_id, stock_status = create_stock_with_sender_receiver_types(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_id=prerequisites["staff_1_user_uuid"],
        sender_type="STAFF",
        receiver_id=prerequisites["staff_2_user_uuid"],
        receiver_type="STAFF",
        transaction_type="DISPATCHED"
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"

    print(f"Stock DISPATCHED (STAFF to STAFF) transaction created with ID: {stock_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock DISPATCHED (STAFF to STAFF) Transaction details ---\n")
        f.write(f"Stock ID: {stock_id}\n")
        f.write(f"Stock Client Reference ID: {stock_client_ref_id}\n")
        f.write(f"Transaction Type: DISPATCHED\n")
        f.write(f"Sender Type: STAFF\n")
        f.write(f"Sender ID (Staff 1 UUID): {prerequisites['staff_1_user_uuid']}\n")
        f.write(f"Receiver Type: STAFF\n")
        f.write(f"Receiver ID (Staff 2 UUID): {prerequisites['staff_2_user_uuid']}\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")


@pytest.mark.positive
def test_search_stock():
    """Test to search for a stock transaction by ID. Creates stock if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    stock_id = extract_id_from_file("Stock ID:")
    if not stock_id:
        # Create stock internally if ID not found
        print("Stock ID not found in file, creating new stock...")
        prerequisites = setup_stock_prerequisites(token, client)
        stock_id, _, _ = create_stock(
            token, client,
            product_variant_id=prerequisites["variant_id_1"],
            project_id=prerequisites["project_id"],
            sender_facility_id=prerequisites["sender_facility_id"],
            receiver_facility_id=prerequisites["receiver_facility_id"],
            transaction_type="RECEIVED"
        )
        print(f"Stock created with ID: {stock_id}")

    stocks = search_stock(token, client, stock_id)
    assert stocks, "No stocks found in search response"

    found_ids = [s["id"] for s in stocks]
    assert stock_id in found_ids, f"Stock {stock_id} not found in search results"
    print(f"Stock found with ID: {stock_id}")


@pytest.mark.positive
def test_create_stock_reconciliation():
    """
    Test to create a stock reconciliation record.
    Internally creates: facility, product variant, project, project resource, project facility, stock
    Then uses those details for stock reconciliation creation.
    """
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Setup stock prerequisites
    print("Setting up prerequisites for stock reconciliation...")
    prerequisites = setup_stock_prerequisites(token, client)

    # Create stock RECEIVED transaction first
    print("Creating stock RECEIVED transaction...")
    stock_id, stock_client_ref_id, stock_status = create_stock(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_facility_id=prerequisites["sender_facility_id"],
        receiver_facility_id=prerequisites["receiver_facility_id"],
        transaction_type="RECEIVED",
        quantity=1000
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"
    print(f"Stock created with ID: {stock_id}")

    # Create stock reconciliation
    print("Creating stock reconciliation...")
    recon_id, recon_client_ref_id, recon_status = create_stock_reconciliation(
        token, client,
        facility_id=prerequisites["receiver_facility_id"],
        product_variant_id=prerequisites["variant_id_1"],
        reference_id=prerequisites["project_id"],
        physical_count=950,
        calculated_count=1000
    )
    assert recon_status in [200, 202], f"Stock Reconciliation creation failed with status: {recon_status}"

    print(f"Stock Reconciliation created with ID: {recon_id}")

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Stock Reconciliation details ---\n")
        f.write(f"Stock Reconciliation ID: {recon_id}\n")
        f.write(f"Stock Reconciliation Client Reference ID: {recon_client_ref_id}\n")
        f.write(f"Facility ID: {prerequisites['receiver_facility_id']}\n")
        f.write(f"Product Variant ID: {prerequisites['variant_id_1']}\n")
        f.write(f"Project ID: {prerequisites['project_id']}\n")
        f.write(f"Physical Count: 950\n")
        f.write(f"Calculated Count: 1000\n")
        f.write(f"Related Stock ID: {stock_id}\n")


@pytest.mark.positive
def test_search_stock_reconciliation():
    """Test to search for a stock reconciliation by ID. Creates stock reconciliation if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    recon_id = extract_id_from_file("Stock Reconciliation ID:")
    if not recon_id:
        # Create stock reconciliation internally if ID not found
        print("Stock Reconciliation ID not found in file, creating new stock reconciliation...")
        prerequisites = setup_stock_prerequisites(token, client)

        # Create stock first
        create_stock(
            token, client,
            product_variant_id=prerequisites["variant_id_1"],
            project_id=prerequisites["project_id"],
            sender_facility_id=prerequisites["sender_facility_id"],
            receiver_facility_id=prerequisites["receiver_facility_id"],
            transaction_type="RECEIVED",
            quantity=1000
        )

        # Create stock reconciliation
        recon_id, _, _ = create_stock_reconciliation(
            token, client,
            facility_id=prerequisites["receiver_facility_id"],
            product_variant_id=prerequisites["variant_id_1"],
            reference_id=prerequisites["project_id"],
            physical_count=950,
            calculated_count=1000
        )
        print(f"Stock Reconciliation created with ID: {recon_id}")

    recons = search_stock_reconciliation(token, client, recon_id)
    assert recons, "No stock reconciliations found in search response"

    found_ids = [r["id"] for r in recons]
    assert recon_id in found_ids, f"Stock Reconciliation {recon_id} not found in search results"
    print(f"Stock Reconciliation found with ID: {recon_id}")


# --- Negative Tests ---

@pytest.mark.negative
def test_create_stock_with_invalid_tenant_id():
    """Negative test: Creating stock with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Get valid IDs from file or use dummy values
    variant_id = extract_id_from_file("Variant ID:") or "PVAR-dummy"
    project_id = extract_id_from_file("Project ID:") or "project-dummy"
    facility_id = extract_id_from_file("Facility ID:") or "F-dummy"

    payload = load_payload("stock", "create_stock.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Stock"]["tenantId"] = invalidTenantId
    payload["Stock"]["clientReferenceId"] = str(uuid.uuid4())
    payload["Stock"]["productVariantId"] = variant_id
    payload["Stock"]["quantity"] = 100
    payload["Stock"]["referenceId"] = project_id
    payload["Stock"]["referenceIdType"] = "PROJECT"
    payload["Stock"]["transactionType"] = "RECEIVED"
    payload["Stock"]["transactionReason"] = "NEW"
    payload["Stock"]["senderType"] = "WAREHOUSE"
    payload["Stock"]["senderId"] = facility_id
    payload["Stock"]["receiverType"] = "WAREHOUSE"
    payload["Stock"]["receiverId"] = facility_id

    url = f"/{STOCK_SERVICE}/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Create stock correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_stock_with_invalid_tenant_id():
    """Negative test: Searching stock with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    stock_id = extract_id_from_file("Stock ID:")
    if not stock_id:
        # Create a new stock if ID not found
        prerequisites = setup_stock_prerequisites(token, client)
        stock_id, _, _ = create_stock(
            token, client,
            product_variant_id=prerequisites["variant_id_1"],
            project_id=prerequisites["project_id"],
            sender_facility_id=prerequisites["sender_facility_id"],
            receiver_facility_id=prerequisites["receiver_facility_id"],
            transaction_type="RECEIVED"
        )

    payload = load_payload("stock", "search_stock.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Stock"]["id"] = [stock_id]

    url = f"/{STOCK_SERVICE}/v1/_search?limit={search_limit}&offset={search_offset}&tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search stock correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_create_stock_reconciliation_with_invalid_tenant_id():
    """Negative test: Creating stock reconciliation with invalid tenantId should fail"""
    import time

    token = get_auth_token("user")
    client = APIClient(token=token)

    # Get valid IDs from file or use dummy values
    facility_id = extract_id_from_file("Facility ID:") or "F-dummy"
    variant_id = extract_id_from_file("Variant ID:") or "PVAR-dummy"
    project_id = extract_id_from_file("Project ID:") or "project-dummy"

    payload = load_payload("stock/stock_recon", "create_stock_recon.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["StockReconciliation"]["tenantId"] = invalidTenantId
    payload["StockReconciliation"]["clientReferenceId"] = str(uuid.uuid4())
    payload["StockReconciliation"]["facilityId"] = facility_id
    payload["StockReconciliation"]["productVariantId"] = variant_id
    payload["StockReconciliation"]["referenceId"] = project_id
    payload["StockReconciliation"]["referenceIdType"] = "PROJECT"
    payload["StockReconciliation"]["physicalCount"] = 100
    payload["StockReconciliation"]["calculatedCount"] = 100
    payload["StockReconciliation"]["commentsOnReconciliation"] = "Negative test"
    payload["StockReconciliation"]["dateOfReconciliation"] = int(time.time() * 1000)

    url = f"/{STOCK_SERVICE}/reconciliation/v1/_create"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Create stock reconciliation correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_stock_reconciliation_with_invalid_tenant_id():
    """Negative test: Searching stock reconciliation with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    recon_id = extract_id_from_file("Stock Reconciliation ID:")
    if not recon_id:
        # Create a new stock reconciliation if ID not found
        prerequisites = setup_stock_prerequisites(token, client)

        # Create stock first
        create_stock(
            token, client,
            product_variant_id=prerequisites["variant_id_1"],
            project_id=prerequisites["project_id"],
            sender_facility_id=prerequisites["sender_facility_id"],
            receiver_facility_id=prerequisites["receiver_facility_id"],
            transaction_type="RECEIVED",
            quantity=1000
        )

        # Create stock reconciliation
        recon_id, _, _ = create_stock_reconciliation(
            token, client,
            facility_id=prerequisites["receiver_facility_id"],
            product_variant_id=prerequisites["variant_id_1"],
            reference_id=prerequisites["project_id"],
            physical_count=950,
            calculated_count=1000
        )

    payload = load_payload("stock/stock_recon", "search_stock_recon.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["StockReconciliation"]["id"] = [recon_id]

    url = f"/{STOCK_SERVICE}/reconciliation/v1/_search?limit={search_limit}&offset={search_offset}&tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search stock reconciliation correctly rejected with status: {response.status_code}")


@pytest.mark.positive
def test_update_stock():
    """Test to update a stock transaction. Creates all dependencies internally first, then updates quantity."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Setting up prerequisites for stock update test...")
    prerequisites = setup_stock_prerequisites(token, client)

    # Step 2: Create stock RECEIVED transaction
    print("Creating stock RECEIVED transaction...")
    stock_data, stock_status = create_stock_full(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_facility_id=prerequisites["sender_facility_id"],
        receiver_facility_id=prerequisites["receiver_facility_id"],
        transaction_type="RECEIVED",
        quantity=500
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"
    print(f"Stock created with ID: {stock_data['id']}")

    # Step 3: Use create response data directly (async APIs may not be immediately searchable)
    original_quantity = stock_data.get("quantity", 0)
    print(f"Original quantity: {original_quantity}")

    # Step 4: Update the stock (change quantity)
    new_quantity = 750
    response = update_stock(token, client, stock_data, new_quantity)
    assert response.status_code in [200, 202], f"Stock update failed: {response.text}"

    # Step 5: Verify update
    updated_stock = response.json()["Stock"]
    assert updated_stock["quantity"] == new_quantity, f"Quantity not updated. Expected {new_quantity}, got {updated_stock.get('quantity')}"
    print(f"Stock updated successfully. Quantity changed from {original_quantity} to {new_quantity}")


@pytest.mark.positive
def test_update_stock_reconciliation():
    """Test to update a stock reconciliation. Creates all dependencies internally first, then updates physicalCount."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create all dependencies internally
    print("Setting up prerequisites for stock reconciliation update test...")
    prerequisites = setup_stock_prerequisites(token, client)

    # Step 2: Create stock RECEIVED transaction first
    print("Creating stock RECEIVED transaction...")
    stock_id, stock_client_ref_id, stock_status = create_stock(
        token, client,
        product_variant_id=prerequisites["variant_id_1"],
        project_id=prerequisites["project_id"],
        sender_facility_id=prerequisites["sender_facility_id"],
        receiver_facility_id=prerequisites["receiver_facility_id"],
        transaction_type="RECEIVED",
        quantity=1000
    )
    assert stock_status in [200, 202], f"Stock creation failed with status: {stock_status}"
    print(f"Stock created with ID: {stock_id}")

    # Step 3: Create stock reconciliation
    print("Creating stock reconciliation...")
    recon_data, recon_status = create_stock_reconciliation_full(
        token, client,
        facility_id=prerequisites["receiver_facility_id"],
        product_variant_id=prerequisites["variant_id_1"],
        reference_id=prerequisites["project_id"],
        physical_count=950,
        calculated_count=1000
    )
    assert recon_status in [200, 202], f"Stock Reconciliation creation failed with status: {recon_status}"
    print(f"Stock Reconciliation created with ID: {recon_data['id']}")

    # Step 4: Use create response data directly (async APIs may not be immediately searchable)
    original_physical_count = recon_data.get("physicalCount", 0)
    print(f"Original physical count: {original_physical_count}")

    # Step 5: Update the stock reconciliation (change physicalCount)
    new_physical_count = 980
    response = update_stock_reconciliation(token, client, recon_data, new_physical_count)
    assert response.status_code in [200, 202], f"Stock Reconciliation update failed: {response.text}"

    # Step 6: Verify update
    updated_recon = response.json()["StockReconciliation"]
    assert updated_recon["physicalCount"] == new_physical_count, f"Physical count not updated. Expected {new_physical_count}, got {updated_recon.get('physicalCount')}"
    print(f"Stock Reconciliation updated successfully. Physical count changed from {original_physical_count} to {new_physical_count}")


# --- Reusable Functions ---

# --- Helper Functions for Setup ---

def _create_facility_with_assert(token, client, name="facility"):
    """Helper to create a facility with assertion."""
    print(f"Creating {name}...")
    response = create_facility(token, client)
    assert response.status_code in [200, 202], f"{name} creation failed: {response.text}"
    facility_id = response.json()["Facility"]["id"]
    print(f"{name} created with ID: {facility_id}")
    return facility_id


def _create_employee_with_assert(token, client, name="employee"):
    """Helper to create an employee with assertion."""
    print(f"Creating {name}...")
    employee_code, _, _, userservice_uuid, status = create_employee(token, client)
    assert status in [200, 202], f"{name} creation failed with status: {status}"
    print(f"{name} created with code: {employee_code}, userServiceUuid: {userservice_uuid}")
    return userservice_uuid


def _create_project_staff_with_assert(token, client, project_id, userservice_uuid, name="project staff"):
    """Helper to create project staff with assertion."""
    print(f"Creating {name}...")
    staff_id, status = create_project_staff(token, client, project_id, userservice_uuid)
    assert status in [200, 202], f"{name} creation failed with status: {status}"
    print(f"{name} created with ID: {staff_id}")
    return staff_id


def _setup_base_stock_prerequisites(token, client):
    """
    Setup base prerequisites for stock creation.
    Creates: product variants, project, project resources.

    Returns:
        Dictionary containing:
        - variant_id_1, variant_id_2
        - project_id
        - resource_id_1, resource_id_2
    """
    # Create product variants
    print("Creating product variant 1...")
    variant_response_1 = create_product_variant(token, client)
    assert variant_response_1.status_code in [200, 202], f"Product Variant 1 creation failed: {variant_response_1.text}"
    variant_id_1 = variant_response_1.json()["ProductVariant"][0]["id"]
    print(f"Product Variant 1 created with ID: {variant_id_1}")

    print("Creating product variant 2...")
    variant_response_2 = create_product_variant(token, client)
    assert variant_response_2.status_code in [200, 202], f"Product Variant 2 creation failed: {variant_response_2.text}"
    variant_id_2 = variant_response_2.json()["ProductVariant"][0]["id"]
    print(f"Product Variant 2 created with ID: {variant_id_2}")

    # Create project with the product variants
    print("Creating project...")
    project_id, project_status = create_individual_project(token, client, boundaryType, boundaryCode, variant_id_1, variant_id_2)
    assert project_status in [200, 202], f"Project creation failed with status: {project_status}"
    print(f"Project created with ID: {project_id}")

    # Create project resource mappings
    print("Creating project resource for variant 1...")
    resource_id_1, resource_status_1 = create_project_resource(token, client, project_id, variant_id_1)
    assert resource_status_1 in [200, 202], f"Project Resource 1 creation failed with status: {resource_status_1}"
    print(f"Project Resource 1 created with ID: {resource_id_1}")

    print("Creating project resource for variant 2...")
    resource_id_2, resource_status_2 = create_project_resource(token, client, project_id, variant_id_2)
    assert resource_status_2 in [200, 202], f"Project Resource 2 creation failed with status: {resource_status_2}"
    print(f"Project Resource 2 created with ID: {resource_id_2}")

    return {
        "variant_id_1": variant_id_1,
        "variant_id_2": variant_id_2,
        "project_id": project_id,
        "resource_id_1": resource_id_1,
        "resource_id_2": resource_id_2
    }


# --- Setup Functions ---

def setup_stock_prerequisites(token, client):
    """
    Setup all prerequisites for stock creation between two facilities.
    Creates: facilities, product variants, project, project resources, project facilities.
    """
    # Create two facilities
    sender_facility_id = _create_facility_with_assert(token, client, "Sender Facility")
    receiver_facility_id = _create_facility_with_assert(token, client, "Receiver Facility")

    # Setup base prerequisites (variants, project, resources)
    base = _setup_base_stock_prerequisites(token, client)

    # Create project facility mappings
    print("Creating project facility for sender...")
    project_facility_id_1, status_1 = create_project_facility(token, client, base["project_id"], sender_facility_id)
    assert status_1 in [200, 202], f"Project Facility 1 creation failed with status: {status_1}"
    print(f"Project Facility 1 created with ID: {project_facility_id_1}")

    print("Creating project facility for receiver...")
    project_facility_id_2, status_2 = create_project_facility(token, client, base["project_id"], receiver_facility_id)
    assert status_2 in [200, 202], f"Project Facility 2 creation failed with status: {status_2}"
    print(f"Project Facility 2 created with ID: {project_facility_id_2}")

    return {
        "sender_facility_id": sender_facility_id,
        "receiver_facility_id": receiver_facility_id,
        "project_facility_id_1": project_facility_id_1,
        "project_facility_id_2": project_facility_id_2,
        **base
    }


def setup_stock_prerequisites_with_staff(token, client):
    """
    Setup all prerequisites for stock creation with a project staff and facility.
    Creates: employee, facility, product variants, project, project resources, project facility, project staff.
    """
    # Create employee and facility
    userservice_uuid = _create_employee_with_assert(token, client, "Employee")
    receiver_facility_id = _create_facility_with_assert(token, client, "Receiver Facility")

    # Setup base prerequisites (variants, project, resources)
    base = _setup_base_stock_prerequisites(token, client)

    # Create project facility mapping
    print("Creating project facility for receiver...")
    project_facility_id, status = create_project_facility(token, client, base["project_id"], receiver_facility_id)
    assert status in [200, 202], f"Project Facility creation failed with status: {status}"
    print(f"Project Facility created with ID: {project_facility_id}")

    # Create project staff
    project_staff_id = _create_project_staff_with_assert(token, client, base["project_id"], userservice_uuid, "Project Staff")

    return {
        "staff_user_uuid": userservice_uuid,
        "project_staff_id": project_staff_id,
        "receiver_facility_id": receiver_facility_id,
        "project_facility_id": project_facility_id,
        **base
    }


def setup_stock_prerequisites_with_two_staff(token, client):
    """
    Setup all prerequisites for stock creation with two project staff members.
    Creates: two employees, product variants, project, project resources, two project staff.
    """
    # Create two employees
    userservice_uuid_1 = _create_employee_with_assert(token, client, "Employee 1")
    userservice_uuid_2 = _create_employee_with_assert(token, client, "Employee 2")

    # Setup base prerequisites (variants, project, resources)
    base = _setup_base_stock_prerequisites(token, client)

    # Create project staff for both employees
    project_staff_id_1 = _create_project_staff_with_assert(token, client, base["project_id"], userservice_uuid_1, "Project Staff 1")
    project_staff_id_2 = _create_project_staff_with_assert(token, client, base["project_id"], userservice_uuid_2, "Project Staff 2")

    return {
        "staff_1_user_uuid": userservice_uuid_1,
        "staff_2_user_uuid": userservice_uuid_2,
        "project_staff_id_1": project_staff_id_1,
        "project_staff_id_2": project_staff_id_2,
        **base
    }


def create_stock(token, client, product_variant_id, project_id, sender_facility_id, receiver_facility_id,
                 quantity=1000, transaction_type="RECEIVED", transaction_reason="NEW"):
    """
    Create a stock transaction.

    Args:
        token: Authentication token
        client: API client instance
        product_variant_id: Product variant ID
        project_id: Project ID (used as referenceId)
        sender_facility_id: Sender facility ID
        receiver_facility_id: Receiver facility ID
        quantity: Stock quantity (default: 1000)
        transaction_type: Transaction type (default: RECEIVED)
        transaction_reason: Transaction reason (default: NEW)

    Returns:
        Tuple of (stock_id, client_reference_id, status_code)
    """
    payload = load_payload("stock", "create_stock.json")
    payload["RequestInfo"] = get_request_info(token)

    # Generate unique client reference ID
    client_reference_id = str(uuid.uuid4())

    # Update stock details
    payload["Stock"]["tenantId"] = tenantId
    payload["Stock"]["clientReferenceId"] = client_reference_id
    payload["Stock"]["productVariantId"] = product_variant_id
    payload["Stock"]["quantity"] = quantity
    payload["Stock"]["referenceId"] = project_id
    payload["Stock"]["referenceIdType"] = "PROJECT"
    payload["Stock"]["transactionType"] = transaction_type
    payload["Stock"]["transactionReason"] = transaction_reason
    payload["Stock"]["senderType"] = "WAREHOUSE"
    payload["Stock"]["senderId"] = sender_facility_id
    payload["Stock"]["receiverType"] = "WAREHOUSE"
    payload["Stock"]["receiverId"] = receiver_facility_id

    url = f"/{STOCK_SERVICE}/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Stock creation failed with status {response.status_code}: {response.text}")

    stock_data = response.json()["Stock"]
    return stock_data["id"], stock_data["clientReferenceId"], response.status_code


def create_stock_with_sender_receiver_types(token, client, product_variant_id, project_id, sender_id, sender_type,
                                            receiver_id, receiver_type, quantity=1000, transaction_type="RECEIVED",
                                            transaction_reason="NEW"):
    """
    Create a stock transaction with custom sender and receiver types.

    Args:
        token: Authentication token
        client: API client instance
        product_variant_id: Product variant ID
        project_id: Project ID (used as referenceId)
        sender_id: Sender ID (facility ID or staff UUID)
        sender_type: Sender type (WAREHOUSE or STAFF)
        receiver_id: Receiver ID (facility ID or staff UUID)
        receiver_type: Receiver type (WAREHOUSE or STAFF)
        quantity: Stock quantity (default: 1000)
        transaction_type: Transaction type (default: RECEIVED)
        transaction_reason: Transaction reason (default: NEW)

    Returns:
        Tuple of (stock_id, client_reference_id, status_code)
    """
    payload = load_payload("stock", "create_stock.json")
    payload["RequestInfo"] = get_request_info(token)

    # Generate unique client reference ID
    client_reference_id = str(uuid.uuid4())

    # Update stock details
    payload["Stock"]["tenantId"] = tenantId
    payload["Stock"]["clientReferenceId"] = client_reference_id
    payload["Stock"]["productVariantId"] = product_variant_id
    payload["Stock"]["quantity"] = quantity
    payload["Stock"]["referenceId"] = project_id
    payload["Stock"]["referenceIdType"] = "PROJECT"
    payload["Stock"]["transactionType"] = transaction_type
    payload["Stock"]["transactionReason"] = transaction_reason
    payload["Stock"]["senderType"] = sender_type
    payload["Stock"]["senderId"] = sender_id
    payload["Stock"]["receiverType"] = receiver_type
    payload["Stock"]["receiverId"] = receiver_id

    url = f"/{STOCK_SERVICE}/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Stock creation failed with status {response.status_code}: {response.text}")

    stock_data = response.json()["Stock"]
    return stock_data["id"], stock_data["clientReferenceId"], response.status_code


def search_stock(token, client, stock_id):
    """
    Search for a stock transaction by ID.

    Args:
        token: Authentication token
        client: API client instance
        stock_id: Stock ID to search for

    Returns:
        List of stocks found
    """
    payload = load_payload("stock", "search_stock.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Stock"]["id"] = [stock_id]

    url = f"/{STOCK_SERVICE}/v1/_search?limit={search_limit}&offset={search_offset}&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code != 200:
        raise Exception(f"Stock search failed with status {response.status_code}: {response.text}")

    return response.json().get("Stock", [])


def create_stock_reconciliation(token, client, facility_id, product_variant_id, reference_id,
                                 physical_count=100, calculated_count=110):
    """
    Create a stock reconciliation record.

    Args:
        token: Authentication token
        client: API client instance
        facility_id: Facility ID for reconciliation
        product_variant_id: Product variant ID
        reference_id: Reference ID (typically project ID)
        physical_count: Physical count of stock (default: 100)
        calculated_count: Calculated/expected count of stock (default: 110)

    Returns:
        Tuple of (reconciliation_id, client_reference_id, status_code)
    """
    import time

    payload = load_payload("stock/stock_recon", "create_stock_recon.json")
    payload["RequestInfo"] = get_request_info(token)

    # Generate unique client reference ID
    client_reference_id = str(uuid.uuid4())

    # Update stock reconciliation details
    payload["StockReconciliation"]["tenantId"] = tenantId
    payload["StockReconciliation"]["clientReferenceId"] = client_reference_id
    payload["StockReconciliation"]["facilityId"] = facility_id
    payload["StockReconciliation"]["productVariantId"] = product_variant_id
    payload["StockReconciliation"]["referenceId"] = reference_id
    payload["StockReconciliation"]["referenceIdType"] = "PROJECT"
    payload["StockReconciliation"]["physicalCount"] = physical_count
    payload["StockReconciliation"]["calculatedCount"] = calculated_count
    payload["StockReconciliation"]["commentsOnReconciliation"] = "Automated test reconciliation"
    payload["StockReconciliation"]["dateOfReconciliation"] = int(time.time() * 1000)

    url = f"/{STOCK_SERVICE}/reconciliation/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Stock Reconciliation creation failed with status {response.status_code}: {response.text}")

    recon_data = response.json()["StockReconciliation"]
    return recon_data["id"], recon_data["clientReferenceId"], response.status_code


def search_stock_reconciliation(token, client, recon_id):
    """
    Search for a stock reconciliation by ID.

    Args:
        token: Authentication token
        client: API client instance
        recon_id: Stock Reconciliation ID to search for

    Returns:
        List of stock reconciliations found
    """
    payload = load_payload("stock/stock_recon", "search_stock_recon.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["StockReconciliation"]["id"] = [recon_id]

    url = f"/{STOCK_SERVICE}/reconciliation/v1/_search?limit={search_limit}&offset={search_offset}&tenantId={tenantId}"
    response = client.post(url, payload)

    if response.status_code != 200:
        raise Exception(f"Stock Reconciliation search failed with status {response.status_code}: {response.text}")

    return response.json().get("StockReconciliation", [])


def create_stock_full(token, client, product_variant_id, project_id, sender_facility_id, receiver_facility_id,
                      quantity=1000, transaction_type="RECEIVED", transaction_reason="NEW"):
    """
    Create a stock transaction and return full data for update operations.

    Returns:
        Tuple of (stock_data, status_code)
    """
    payload = load_payload("stock", "create_stock.json")
    payload["RequestInfo"] = get_request_info(token)

    # Generate unique client reference ID
    client_reference_id = str(uuid.uuid4())

    # Update stock details
    payload["Stock"]["tenantId"] = tenantId
    payload["Stock"]["clientReferenceId"] = client_reference_id
    payload["Stock"]["productVariantId"] = product_variant_id
    payload["Stock"]["quantity"] = quantity
    payload["Stock"]["referenceId"] = project_id
    payload["Stock"]["referenceIdType"] = "PROJECT"
    payload["Stock"]["transactionType"] = transaction_type
    payload["Stock"]["transactionReason"] = transaction_reason
    payload["Stock"]["senderType"] = "WAREHOUSE"
    payload["Stock"]["senderId"] = sender_facility_id
    payload["Stock"]["receiverType"] = "WAREHOUSE"
    payload["Stock"]["receiverId"] = receiver_facility_id

    url = f"/{STOCK_SERVICE}/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Stock creation failed with status {response.status_code}: {response.text}")

    return response.json()["Stock"], response.status_code


def create_stock_reconciliation_full(token, client, facility_id, product_variant_id, reference_id,
                                      physical_count=100, calculated_count=110):
    """
    Create a stock reconciliation and return full data for update operations.

    Returns:
        Tuple of (reconciliation_data, status_code)
    """
    import time

    payload = load_payload("stock/stock_recon", "create_stock_recon.json")
    payload["RequestInfo"] = get_request_info(token)

    # Generate unique client reference ID
    client_reference_id = str(uuid.uuid4())

    # Update stock reconciliation details
    payload["StockReconciliation"]["tenantId"] = tenantId
    payload["StockReconciliation"]["clientReferenceId"] = client_reference_id
    payload["StockReconciliation"]["facilityId"] = facility_id
    payload["StockReconciliation"]["productVariantId"] = product_variant_id
    payload["StockReconciliation"]["referenceId"] = reference_id
    payload["StockReconciliation"]["referenceIdType"] = "PROJECT"
    payload["StockReconciliation"]["physicalCount"] = physical_count
    payload["StockReconciliation"]["calculatedCount"] = calculated_count
    payload["StockReconciliation"]["commentsOnReconciliation"] = "Automated test reconciliation"
    payload["StockReconciliation"]["dateOfReconciliation"] = int(time.time() * 1000)

    url = f"/{STOCK_SERVICE}/reconciliation/v1/_create"
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Stock Reconciliation creation failed with status {response.status_code}: {response.text}")

    return response.json()["StockReconciliation"], response.status_code


def update_stock(token, client, stock_data, new_quantity):
    """
    Update a stock transaction's quantity.

    Args:
        stock_data: Full stock object from create response
        new_quantity: New quantity value to set
    """
    payload = load_payload("stock", "update_stock.json")

    # Copy required fields from the created stock
    payload["Stock"]["id"] = stock_data["id"]
    payload["Stock"]["tenantId"] = stock_data["tenantId"]
    payload["Stock"]["clientReferenceId"] = stock_data["clientReferenceId"]
    payload["Stock"]["rowVersion"] = stock_data["rowVersion"]
    payload["Stock"]["auditDetails"] = stock_data["auditDetails"]
    payload["Stock"]["clientAuditDetails"] = stock_data.get("clientAuditDetails")
    payload["Stock"]["productVariantId"] = stock_data["productVariantId"]
    payload["Stock"]["referenceId"] = stock_data["referenceId"]
    payload["Stock"]["referenceIdType"] = stock_data["referenceIdType"]
    payload["Stock"]["transactionType"] = stock_data["transactionType"]
    payload["Stock"]["transactionReason"] = stock_data.get("transactionReason")
    payload["Stock"]["senderId"] = stock_data["senderId"]
    payload["Stock"]["senderType"] = stock_data["senderType"]
    payload["Stock"]["receiverId"] = stock_data["receiverId"]
    payload["Stock"]["receiverType"] = stock_data["receiverType"]
    payload["Stock"]["quantity"] = new_quantity
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{STOCK_SERVICE}/v1/_update"
    response = client.post(url, payload)
    return response


def update_stock_reconciliation(token, client, recon_data, new_physical_count):
    """
    Update a stock reconciliation's physical count.

    Args:
        recon_data: Full stock reconciliation object from create response
        new_physical_count: New physical count value to set
    """
    import time

    payload = load_payload("stock/stock_recon", "update_stock_recon.json")

    # Copy required fields from the created reconciliation
    payload["StockReconciliation"]["id"] = recon_data["id"]
    payload["StockReconciliation"]["tenantId"] = recon_data["tenantId"]
    payload["StockReconciliation"]["clientReferenceId"] = recon_data["clientReferenceId"]
    payload["StockReconciliation"]["rowVersion"] = recon_data["rowVersion"]
    payload["StockReconciliation"]["auditDetails"] = recon_data["auditDetails"]
    payload["StockReconciliation"]["clientAuditDetails"] = recon_data.get("clientAuditDetails")
    payload["StockReconciliation"]["facilityId"] = recon_data["facilityId"]
    payload["StockReconciliation"]["productVariantId"] = recon_data["productVariantId"]
    payload["StockReconciliation"]["referenceId"] = recon_data["referenceId"]
    payload["StockReconciliation"]["referenceIdType"] = recon_data["referenceIdType"]
    payload["StockReconciliation"]["calculatedCount"] = recon_data["calculatedCount"]
    payload["StockReconciliation"]["physicalCount"] = new_physical_count
    payload["StockReconciliation"]["commentsOnReconciliation"] = "Updated via automated test"
    payload["StockReconciliation"]["dateOfReconciliation"] = int(time.time() * 1000)
    payload["RequestInfo"] = get_request_info(token)

    url = f"/{STOCK_SERVICE}/reconciliation/v1/_update"
    response = client.post(url, payload)
    return response
