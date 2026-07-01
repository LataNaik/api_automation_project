from utils.config import tenantId as _tenantId
from utils.auth import get_user_info

def get_request_info(token: str, service: str = "user") -> dict:
    user_info = get_user_info(service)
    return {
        "apiId": "org.egov.household",
        "ver": "1.0",
        "ts": 0,
        "action": "create",
        "msgId": "202507150001",
        "authToken": token,
        "userInfo": user_info if user_info else {
            "id": 0,
            "userName": "",
            "type": "EMPLOYEE",
            "uuid": "",
            "tenantId": _tenantId,
            "roles": []
        }
    }
