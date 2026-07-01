import os
import requests
from dotenv import load_dotenv
from utils.config import tenantId

# Load environment variables from .env file
load_dotenv(override=True)  # This forces reloading of updated values

_token_cache: dict[str, str] = {}
_user_info_cache: dict[str, dict] = {}

def get_auth_token(service: str):
    if service in _token_cache:
        return _token_cache[service]

    url = os.getenv("BASE_URL") + "/user/oauth/token"

    payload = {
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "grant_type": "password",
        "scope": "read",
        "tenantId": tenantId,
        "userType": os.getenv("USERTYPE")
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": os.getenv("CLIENT_AUTH_HEADER"),
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    assert response.status_code == 200, f"Auth failed: {response.text}"
    data = response.json()
    token = data.get("access_token")
    _token_cache[service] = token
    _user_info_cache[service] = data.get("UserRequest", {})
    return token


def get_user_info(service: str) -> dict:
    if service not in _user_info_cache:
        get_auth_token(service)
    return _user_info_cache.get(service, {})


def clear_token_cache():
    _token_cache.clear()
    _user_info_cache.clear()
