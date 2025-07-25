from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.search_helpers import search_entity, extract_id_from_file


# --- Test functions ---

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


def test_search_product():
    token = get_auth_token("user")
    client = APIClient(token=token)

    productId = extract_id_from_file("Product ID:")
    assert productId, "Product ID not found in file"

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


def test_search_product_variant():
    token = get_auth_token("user")
    client = APIClient(token=token)

    variantId = extract_id_from_file("Variant ID:")
    assert variantId, "Variant ID not found in file"

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


# --- Reusable Functions ---

def create_product(token, client):
    payload = load_payload("product", "create_product.json")
    payload["RequestInfo"] = get_request_info(token)
    return client.post("/product/v1/_create", payload)


def create_product_variant(token, client):
    product_res = create_product(token, client)
    assert product_res.status_code in [200, 202], f"Product creation for variant failed: {product_res.text}"

    productId = product_res.json()["Product"][0]["id"]

    payload = load_payload("product", "create_productVariant.json")
    payload["ProductVariant"][0]["productId"] = productId
    payload["RequestInfo"] = get_request_info(token)
    return client.post("/product/variant/v1/_create", payload)
