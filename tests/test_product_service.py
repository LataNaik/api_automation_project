import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file
from utils.config import invalidTenantId


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
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print("Negative test passed: Creating product with invalid tenantId returned 401")


@pytest.mark.negative
def test_create_product_variant_with_invalid_tenant_id():
    """Negative test: Creating product variant with invalid tenantId should fail"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = create_product_variant(token, client, tenant_id=invalidTenantId)

    # Should fail with 401 Unauthorized
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
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

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
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

    assert response.status_code in [400, 401, 403], f"Expected error status code, got: {response.status_code}"
    print(f"Search correctly rejected with status: {response.status_code}")


# --- Reusable Functions ---

def create_product(token, client, tenant_id=None):
    """
    Create a product.

    Args:
        tenant_id: Pass None to use default, or provide custom tenantId for negative testing
    """
    payload = load_payload("product", "create_product.json")
    payload["RequestInfo"] = get_request_info(token)

    # Override tenantId if provided (for negative testing)
    if tenant_id is not None:
        payload["Product"][0]["tenantId"] = tenant_id

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
    payload["RequestInfo"] = get_request_info(token)

    # Override tenantId if provided (for negative testing)
    if tenant_id is not None:
        payload["ProductVariant"][0]["tenantId"] = tenant_id

    return client.post("/product/variant/v1/_create", payload)
