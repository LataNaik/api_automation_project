import os
from dotenv import load_dotenv

load_dotenv(override=True)  # This forces reloading of updated values

BASE_URL = os.getenv("BASE_URL")
tenantId = os.getenv("TENANTID", "mz")

search_limit = os.getenv("SEARCH_LIMIT", "100")
search_offset = os.getenv("SEARCH_OFFSET", "0")
hierarchyType = os.getenv("HIERARCHYTYPE")
boundaryCode = os.getenv("BOUNDARY_CODE")
boundaryType=os.getenv("BOUNDARY_TYPE")

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