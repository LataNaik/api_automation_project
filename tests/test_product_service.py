import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import tenantId, invalidTenantId


# --- Test functions ---

@pytest.mark.positive
def test_create_product():
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_product(token, client)
    assert res.status_code in [200, 202], f"Product creation failed: {res.text}"

    productId = res.json()["Product"][0]["id"]
    assert productId, "Product ID not found in response"
    print("Product created with ID:", productId)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Product details ---\n")
        f.write(f"Product ID: {productId}\n")


@pytest.mark.positive
def test_create_product_variant():
    token = get_auth_token("user")
    client = APIClient(token=token)

    variant_res = create_product_variant(token, client)
    assert variant_res.status_code in [200, 202], f"Variant creation failed: {variant_res.text}"

    variantId = variant_res.json()["ProductVariant"][0]["id"]
    assert variantId, "Variant ID was not created"
    print("Product Variant created with ID:", variantId)

    with open("output/ids.txt", "a") as f:
        f.write("\n--- Product Variant details ---\n")
        f.write(f"Variant ID: {variantId}\n")


@pytest.mark.positive
def test_search_product():
    """Test to search for a product by ID. Creates product if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    productId = extract_id_from_file("Product ID:")
    if not productId:
        # Create product internally if ID not found
        print("Product ID not found in file, creating new product...")
        res = create_product(token, client)
        assert res.status_code in [200, 202], f"Product creation failed: {res.text}"
        productId = res.json()["Product"][0]["id"]
        print(f"Product created with ID: {productId}")

    products = search_entity(
        entity_type="product",
        token=token,
        client=client,
        entity_id=productId,
        payload_file="search_product.json",
        endpoint="/product/v1/_search",
        response_key="Product"
    )

    assert productId in [p["id"] for p in products], "Product not found"
    print("Product found with ID:", productId)


@pytest.mark.positive
def test_search_product_variant():
    """Test to search for a product variant by ID. Creates variant if ID not found in file."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    variantId = extract_id_from_file("Variant ID:")
    if not variantId:
        # Create product variant internally if ID not found
        print("Variant ID not found in file, creating new product variant...")
        variant_res = create_product_variant(token, client)
        assert variant_res.status_code in [200, 202], f"Variant creation failed: {variant_res.text}"
        variantId = variant_res.json()["ProductVariant"][0]["id"]
        print(f"Product Variant created with ID: {variantId}")

    variants = search_entity(
        entity_type="product",
        token=token,
        client=client,
        entity_id=variantId,
        payload_file="search_productVariant.json",
        endpoint="/product/variant/v1/_search",
        response_key="ProductVariant"
    )

    assert variantId in [v["id"] for v in variants], "Product Variant not found"
    print("Product Variant found with ID:", variantId)


@pytest.mark.negative
def test_create_product_with_invalid_tenant_id():
    """Negative test: Creating product with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_product(token, client, tenant_id=invalidTenantId)

    # Should fail with 401 Unauthorized
    assert res.status_code == 401, f"Expected  4xx, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating product with invalid tenantId returned 401")


@pytest.mark.negative
def test_create_product_variant_with_invalid_tenant_id():
    """Negative test: Creating product variant with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_product_variant(token, client, tenant_id=invalidTenantId)

    # Should fail with 401 Unauthorized
    assert res.status_code == 401, f"Expected  4xx, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating product variant with invalid tenantId returned 401")


@pytest.mark.negative
def test_create_product_variant_without_productId():
    """Negative test: Creating product variant without productId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_product_variant(token, client, product_id=None)

    # Should fail with 400 Bad Request
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating product variant without productId returned 400")


@pytest.mark.negative
def test_search_product_with_invalid_tenant_id():
    """Negative test: Searching product with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    product_id = extract_id_from_file("Product ID:")
    if not product_id:
        # Create a new product if ID not found
        res = create_product(token, client)
        assert res.status_code in [200, 202], f"Product creation failed: {res.text}"
        product_id = res.json()["Product"][0]["id"]

    payload = load_payload("product", "search_product.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Product"]["id"] = [product_id]

    url = f"/product/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code == 401, f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.negative
def test_search_product_variant_with_invalid_tenant_id():
    """Negative test: Searching product variant with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    variant_id = extract_id_from_file("Variant ID:")
    if not variant_id:
        # Create a new product variant if ID not found
        res = create_product_variant(token, client)
        assert res.status_code in [200, 202], f"Product Variant creation failed: {res.text}"
        variant_id = res.json()["ProductVariant"][0]["id"]

    payload = load_payload("product", "search_productVariant.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["ProductVariant"]["id"] = [variant_id]

    url = f"/product/variant/v1/_search?tenantId={invalidTenantId}"
    response = client.post(url, payload)

    assert response.status_code == 401, f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


@pytest.mark.positive
def test_update_product():
    """Test to update a product. Creates product internally first, then updates the name."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create product internally
    print("Creating product for update test...")
    product_data, product_status = create_product_full(token, client)
    assert product_status in [200, 202], f"Product creation failed with status: {product_status}"
    print(f"Product created with ID: {product_data['id']}")

    # Step 2: Use create response data directly
    original_name = product_data.get("name", "")
    print(f"Original name: {original_name}")

    # Step 3: Update the product (change name)
    new_name = f"Updated-{original_name}"
    response = update_product(token, client, product_data, new_name)
    assert response.status_code in [200, 202], f"Product update failed: {response.text}"

    # Step 4: Verify update
    updated_product = response.json()["Product"][0]
    assert updated_product["name"] == new_name, f"Name not updated. Expected {new_name}, got {updated_product.get('name')}"
    print(f"Product updated successfully. Name changed from '{original_name}' to '{new_name}'")


@pytest.mark.positive
def test_update_product_variant():
    """Test to update a product variant. Creates product and variant internally first, then updates the variation."""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Step 1: Create product variant internally
    print("Creating product variant for update test...")
    variant_data, variant_status = create_product_variant_full(token, client)
    assert variant_status in [200, 202], f"Product Variant creation failed with status: {variant_status}"
    print(f"Product Variant created with ID: {variant_data['id']}")

    # Step 2: Use create response data directly
    original_variation = variant_data.get("variation", "")
    print(f"Original variation: {original_variation}")

    # Step 3: Update the product variant (change variation)
    new_variation = f"Updated-{original_variation}"
    response = update_product_variant(token, client, variant_data, new_variation)
    assert response.status_code in [200, 202], f"Product Variant update failed: {response.text}"

    # Step 4: Verify update
    updated_variant = response.json()["ProductVariant"][0]
    assert updated_variant["variation"] == new_variation, f"Variation not updated. Expected {new_variation}, got {updated_variant.get('variation')}"
    print(f"Product Variant updated successfully. Variation changed from '{original_variation}' to '{new_variation}'")


# --- Reusable Functions ---

def create_product(token, client, tenant_id=None):
    """
    Create a product.

    Args:
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
    """
    payload = load_payload("product", "create_product.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Product"][0]["tenantId"] = tenant_id if tenant_id is not None else tenantId

    return client.post("/product/v1/_create", payload)


def create_product_variant(token, client, tenant_id=None, product_id="create"):
    """
    Create a product variant.

    Args:
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
        product_id: Pass "create" to create new product, None to skip, or provide existing ID
    """
    # Create or use provided product
    if product_id == "create":
        product_res = create_product(token, client)
        assert product_res.status_code in [200, 202], f"Product creation for variant failed: {product_res.text}"
        productId = product_res.json()["Product"][0]["id"]
    else:
        productId = product_id

    payload = load_payload("product", "create_productVariant.json")
    payload["ProductVariant"][0]["productId"] = productId
    payload["ProductVariant"][0]["tenantId"] = tenant_id if tenant_id is not None else tenantId
    payload["RequestInfo"] = get_request_info(token)

    return client.post("/product/variant/v1/_create", payload)


def create_product_full(token, client):
    """
    Create a product and return full data for update operations.

    Returns:
        Tuple of (product_data, status_code)
    """
    payload = load_payload("product", "create_product.json")
    payload["Product"][0]["tenantId"] = tenantId
    payload["RequestInfo"] = get_request_info(token)

    response = client.post("/product/v1/_create", payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Product creation failed with status {response.status_code}: {response.text}")

    return response.json()["Product"][0], response.status_code


def create_product_variant_full(token, client):
    """
    Create a product variant and return full data for update operations.

    Returns:
        Tuple of (variant_data, status_code)
    """
    # Create product first
    product_res = create_product(token, client)
    if product_res.status_code not in [200, 202]:
        raise Exception(f"Product creation for variant failed: {product_res.text}")
    productId = product_res.json()["Product"][0]["id"]

    payload = load_payload("product", "create_productVariant.json")
    payload["ProductVariant"][0]["productId"] = productId
    payload["ProductVariant"][0]["tenantId"] = tenantId
    payload["RequestInfo"] = get_request_info(token)

    response = client.post("/product/variant/v1/_create", payload)

    if response.status_code not in [200, 202]:
        raise Exception(f"Product Variant creation failed with status {response.status_code}: {response.text}")

    return response.json()["ProductVariant"][0], response.status_code


def update_product(token, client, product_data, new_name):
    """
    Update a product's name.

    Args:
        product_data: Full product object from create response
        new_name: New name value to set
    """
    payload = load_payload("product", "update_product.json")

    # Copy required fields from the created product
    payload["Product"][0]["id"] = product_data["id"]
    payload["Product"][0]["tenantId"] = product_data["tenantId"]
    payload["Product"][0]["rowVersion"] = product_data["rowVersion"]
    payload["Product"][0]["auditDetails"] = product_data["auditDetails"]
    payload["Product"][0]["type"] = product_data["type"]
    payload["Product"][0]["name"] = new_name
    payload["Product"][0]["manufacturer"] = product_data.get("manufacturer")
    payload["RequestInfo"] = get_request_info(token)

    response = client.post("/product/v1/_update", payload)
    return response


def update_product_variant(token, client, variant_data, new_variation):
    """
    Update a product variant's variation.

    Args:
        variant_data: Full product variant object from create response
        new_variation: New variation value to set
    """
    payload = load_payload("product", "update_productVariant.json")

    # Copy required fields from the created variant
    payload["ProductVariant"][0]["id"] = variant_data["id"]
    payload["ProductVariant"][0]["tenantId"] = variant_data["tenantId"]
    payload["ProductVariant"][0]["rowVersion"] = variant_data["rowVersion"]
    payload["ProductVariant"][0]["auditDetails"] = variant_data["auditDetails"]
    payload["ProductVariant"][0]["productId"] = variant_data["productId"]
    payload["ProductVariant"][0]["sku"] = variant_data.get("sku")
    payload["ProductVariant"][0]["variation"] = new_variation
    payload["RequestInfo"] = get_request_info(token)

    response = client.post("/product/variant/v1/_update", payload)
    return response
