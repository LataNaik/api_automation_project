from utils.auth import get_auth_token
from utils.config import BASE_URL
import requests
import time
import os

# eventual-consistency slack: persisters return 202 then write async to DB.
# downstream tests immediately reference the just-created entity, so we pause
# briefly when a response indicates async acceptance.
_ASYNC_DELAY_S = float(os.getenv("ASYNC_PERSISTER_DELAY", "6.0"))


def _maybe_wait_for_persist(resp):
    if resp.status_code == 202:
        time.sleep(_ASYNC_DELAY_S)
    return resp


class APIClient:
    def __init__(self, service=None, token=None):
        if not token and service:
            token = get_auth_token(service)
        elif not token:
            raise ValueError("Either 'service' or 'token' must be provided")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def get(self, endpoint):
        return requests.get(BASE_URL + endpoint, headers=self.headers)

    def post(self, endpoint, data):
        return _maybe_wait_for_persist(
            requests.post(BASE_URL + endpoint, headers=self.headers, json=data)
        )

    def put(self, endpoint, data):
        return _maybe_wait_for_persist(
            requests.put(BASE_URL + endpoint, headers=self.headers, json=data)
        )

    def delete(self, endpoint):
        return requests.delete(BASE_URL + endpoint, headers=self.headers)
