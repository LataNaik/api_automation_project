import os
from dotenv import load_dotenv

load_dotenv(override=True)  # This forces reloading of updated values

BASE_URL = os.getenv("BASE_URL")
tenantId = os.getenv("TENANTID", "mz")

search_limit = os.getenv("SEARCH_LIMIT", "100")
search_offset = os.getenv("SEARCH_OFFSET", "0")
hierarchyType = os.getenv("BOUNDARY_HIERARCHY_CODE")
boundaryCode = os.getenv("BOUNDARY_CODE")
boundaryType = os.getenv("BOUNDARY_TYPE")
boundaryCodeRoot = os.getenv("BOUNDARY_CODE_ROOT")

if not BASE_URL:
    raise ValueError("BASE_URL not found in .env")


# Define reusable params dict
search_params = {
    "limit": search_limit,
    "offset": search_offset,
    "tenantId": tenantId
}

individual=os.getenv("SERVICE_INDIVIDUAL")
project=os.getenv("SERVICE_PROJECT")
mdms=os.getenv("SERVICE_MDMS")
hrms=os.getenv("SERVICE_HRMS")
pgr=os.getenv("SERVICE_PGR")

# PGR service codes fallback (used when MDMS is unavailable)
pgrServiceCodes = [c.strip() for c in os.getenv("PGR_SERVICE_CODES", "").split(",") if c.strip()]

# Invalid values for negative testing
invalidTenantId=os.getenv("INVALID_TENANT_ID", "invalid_tenant")