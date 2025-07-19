import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
tenantId = os.getenv("TENANTID", "mz")

search_limit = os.getenv("SEARCH_LIMIT", "100")
search_offset = os.getenv("SEARCH_OFFSET", "0")

boundaryCode = os.getenv("BOUNDARY_CODE")

if not BASE_URL:
    raise ValueError("BASE_URL not found in .env")


print("Loaded BASE_URL:", BASE_URL)

