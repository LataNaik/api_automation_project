import os
import requests

def get_auth_token(service: str):
    url = os.getenv("BASE_URL") + "/user/oauth/token"

    # Build dynamic payload based on service (role)
    payload = {
        "username": os.getenv(f"{service.upper()}_USERNAME"),
        "password": os.getenv(f"{service.upper()}_PASSWORD"),
        "grant_type": "password",
        "scope": "read",
        "tenantId": os.getenv(f"{service.upper()}_TENANTID"),
        "userType": os.getenv(f"{service.upper()}_USERTYPE")
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": os.getenv("CLIENT_AUTH_HEADER"),
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    assert response.status_code == 200, f"Auth failed: {response.text}"

    token = response.json().get("access_token")
    return token
