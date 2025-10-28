from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import hierarchyType


def test_search_boundary():
    token = get_auth_token("user")
    client = APIClient(token=token)

    res = search_boundary_data(token, client, "mz", "COUNTRY", "MICROPLAN")
    assert res.status_code == 200, f"Boundary search failed: {res.text}"

    data = res.json()
    tenant_boundaries = data.get("TenantBoundary", [])
    assert tenant_boundaries, "No TenantBoundary found in response"

    boundaries = tenant_boundaries[0].get("boundary", [])
    assert boundaries, "No boundary data found in TenantBoundary"

    boundary_info = collect_boundary_info(boundaries)
    assert boundary_info, "No boundary info collected from response"

    print("\n--- Boundary Hierarchy ---")
    for b_type, code in boundary_info:
        print(f"{b_type}: {code}")

    # Save to file
    with open("output/boundaries.txt", "w") as f:
        f.write("--- Boundary Hierarchy ---\n")
        for b_type, code in boundary_info:
            f.write(f"{b_type}: {code}\n")


def collect_boundary_info(boundaries, results=None):
    if results is None:
        results = []
    for b in boundaries:
        results.append((b.get("boundaryType"), b.get("code")))
        if "children" in b and b["children"]:
            collect_boundary_info(b["children"], results)
    return results


def search_boundary_data(token, client, tenant_id, boundary_type, hierarchy_type):
    payload = load_payload("boundary", "search_boundary.json")
    print("hierarchy_type", hierarchy_type)
    payload["RequestInfo"] = get_request_info(token)

    url = (
        f"/boundary-service/boundary-relationships/_search"
        f"?tenantId={tenant_id}&includeChildren=true"
        f"&boundaryType={boundary_type}&hierarchyType={hierarchy_type}"
    )

    response = client.post(url, payload)
    return response
