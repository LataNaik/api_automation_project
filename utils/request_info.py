def get_request_info(token: str) -> dict:
    return {
        "apiId": "org.egov.household",
        "ver": "1.0",
        "ts": 0,
        "action": "create",
        "msgId": "202507150001",
        "authToken": token,
        "userInfo": {
            "id": 16164561,
            "userName": "auto_user",
            "type": "EMPLOYEE",
            "uuid": "ac775061-7078-41b9-83bc-bfd1d064d20b",
            "tenantId": "mz",
            "roles": [
                {
                    "name": "District Supervisor",
                    "code": "DISTRICT_SUPERVISOR",
                    "tenantId": "mz"
                }
            ]
        }
    }
