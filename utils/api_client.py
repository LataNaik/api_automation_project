from utils.auth import get_auth_token
from utils.config import BASE_URL
import requests

class APIClient:
    _last_instance = None

    def __init__(self, service=None, token=None):
        if not token and service:
            token = get_auth_token(service)
        elif not token:
            raise ValueError("Either 'service' or 'token' must be provided")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        # Track the last request/response for failed test logging
        self.last_request = None
        APIClient._last_instance = self

    def _track(self, method, url, payload, response):
        """Store request and response details for failure debugging."""
        self.last_request = {
            "method": method,
            "url": url,
            "request_payload": payload,
            "response_status": response.status_code,
            "response_body": response.text
        }
        return response

    def get(self, endpoint):
        url = BASE_URL + endpoint
        response = requests.get(url, headers=self.headers)
        return self._track("GET", url, None, response)

    def post(self, endpoint, data):
        url = BASE_URL + endpoint
        response = requests.post(url, headers=self.headers, json=data)
        return self._track("POST", url, data, response)

    def put(self, endpoint, data):
        url = BASE_URL + endpoint
        response = requests.put(url, headers=self.headers, json=data)
        return self._track("PUT", url, data, response)

    def delete(self, endpoint):
        url = BASE_URL + endpoint
        response = requests.delete(url, headers=self.headers)
        return self._track("DELETE", url, None, response)