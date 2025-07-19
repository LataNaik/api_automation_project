from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId, search_params


def test_create_product():
    token = get_auth_token("user")  # Or the relevant service role
    client = APIClient("user")  # Injects token automatically

    # Load payload and manually insert dynamic RequestInfo
    payload = load_payload("product", "create_product.json")

    # Inject RequestInfo manually
    payload["RequestInfo"] = get_request_info(token)
    res = client.post("/product/v1/_create", payload)
    assert res.status_code in [200, 202], f"Unexpected response: {res.text}"

    response_data = res.json()
    productId = response_data["Product"][0]["id"]

    with open("output/data.txt", "a") as f:
        f.write("\n--- Product details ---\n")
        f.write(f"Product ID: {productId}\n")


def test_search_product():
    token = get_auth_token("user")
    client = APIClient("user")

    # Extract Household ID from file
    with open("output/data.txt", "r") as f:
        lines = f.readlines()
    
    productId = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("Product ID:")), None)
    assert productId, "Product ID not found in file"

    print("Extracted Product ID:", productId)

    # Load payload and inject dynamic data
    payload = load_payload("product", "search_product.json")
    payload["Product"]["id"] = [productId]
    payload["RequestInfo"] = get_request_info(token)


    # Build query string from params
    query_string = "&".join(f"{k}={v}" for k, v in search_params.items())
    url = f"/product/v1/_search?{query_string}"
    res = client.post(url, payload)

    assert res.status_code == 200, f"Search failed: {res.text}"
    product_data = res.json().get("Product", [])
    assert productId in [h["id"] for h in product_data], "Product not found"


