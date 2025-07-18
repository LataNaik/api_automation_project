import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    raise ValueError("BASE_URL not found in .env")

# Optional other config values:
# AUTH_ENDPOINT = os.getenv("AUTH_ENDPOINT")
# HEADERS = { ... }

print("Loaded BASE_URL:", BASE_URL)

tenantId = os.getenv("TENANTID")
print("Loaded Tenant Id:", tenantId)