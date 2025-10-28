# API Automation Framework

A comprehensive Python-based API automation testing framework for microservices testing using pytest. This framework provides reusable utilities, dynamic payload management, and extensive reporting capabilities.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Services Covered](#services-covered)
- [Writing Tests](#writing-tests)
- [Running Tests](#running-tests)
- [Reporting](#reporting)
- [Utilities Documentation](#utilities-documentation)
- [Best Practices](#best-practices)
- [Git Workflow](#git-workflow)

---

## Overview

This framework is designed to test multiple microservices with a focus on:
- **Modularity**: Reusable utilities for authentication, API calls, and data management
- **Maintainability**: Separation of test logic, payloads, and configuration
- **Extensibility**: Easy addition of new services and test cases
- **Reporting**: Multiple reporting formats (HTML, Allure)
- **Configuration Management**: Environment-based configuration using `.env` files

---

## Project Structure

```
api_automation_project/
├── tests/                          # Test modules
│   ├── test_individual_service.py
│   ├── test_household_service.py
│   ├── test_boundary_service.py
│   ├── test_facility_service.py
│   ├── test_product_service.py
│   ├── test_project_service.py
│   └── test_mdms_service.py
├── utils/                          # Utility modules
│   ├── api_client.py              # HTTP client wrapper
│   ├── auth.py                    # Authentication token management
│   ├── config.py                  # Configuration loader
│   ├── data_loader.py             # Payload loader
│   ├── request_info.py            # Request metadata builder
│   └── search_helpers.py          # Common search operations
├── payloads/                       # JSON payload templates
│   ├── boundary/
│   ├── facility/
│   ├── household/
│   ├── individual/
│   ├── mdms/
│   ├── product/
│   └── project/
├── data/                          # Test input data
│   └── inputs.json
├── output/                        # Test outputs
│   ├── ids.txt                   # Generated entity IDs
│   ├── response.json             # Latest API response
│   └── boundaries.txt            # Boundary data
├── reports/                       # Test reports
│   └── report.html
├── .env                          # Environment configuration
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Architecture

### Core Components

1. **API Client Layer** (`utils/api_client.py`)
   - Abstraction over HTTP requests
   - Automatic authentication header injection
   - Support for GET, POST, PUT, DELETE methods

2. **Authentication Module** (`utils/auth.py`)
   - OAuth2 token acquisition
   - Token caching per service

3. **Configuration Management** (`utils/config.py`)
   - Centralized environment variable loading
   - Reusable search parameters
   - Service-specific configurations

4. **Payload Management** (`utils/data_loader.py`)
   - Dynamic JSON payload loading
   - Template-based payload structure

5. **Request Metadata** (`utils/request_info.py`)
   - Standardized RequestInfo object creation
   - API metadata and user context

6. **Search Helpers** (`utils/search_helpers.py`)
   - Generic search functionality
   - ID extraction from output files
   - Reusable across multiple services

### Test Flow

```
Test Execution
    ↓
Authentication (get_auth_token)
    ↓
API Client Initialization
    ↓
Load Payload Template (data_loader)
    ↓
Inject Dynamic Data (UUID, IDs, etc.)
    ↓
Add RequestInfo
    ↓
API Call (via APIClient)
    ↓
Validate Response (assertions)
    ↓
Store IDs/Data (output files)
    ↓
Generate Reports
```

---

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Virtual Environment**: Recommended for dependency isolation
- **Git**: For version control

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd api_automation_project
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install python-dotenv requests pytest pytest-html pytest-metadata allure-pytest
```

### 4. Configure Environment

Create or update `.env` file with your environment-specific values:

```env
BASE_URL=https://your-api-server.com
USERNAME=your_username
PASSWORD=your_password
TENANTID=your_tenant
USERTYPE=EMPLOYEE
CLIENT_AUTH_HEADER=Basic <base64_encoded_credentials>

SEARCH_LIMIT=200
SEARCH_OFFSET=0

HIERARCHYTYPE=MICROPLAN
BOUNDARY_TYPE=LOCALITY
BOUNDARY_CODE=your_boundary_code
SERVICE_INDIVIDUAL=individual
SERVICE_PROJECT=project
SERVICE_MDMS=mdms-v2
```

### 5. Verify Setup

```bash
pytest tests/ -v
```

---

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_URL` | API base URL | `https://hcm-demo.digit.org` |
| `USERNAME` | API username | `LNMZ` |
| `PASSWORD` | API password | `eGov@1234` |
| `TENANTID` | Tenant identifier | `mz` |
| `USERTYPE` | User type | `EMPLOYEE` |
| `CLIENT_AUTH_HEADER` | Basic auth header for OAuth | `Basic ZWdvdi11c2VyLWNsaWVudDo=` |
| `SEARCH_LIMIT` | Default search limit | `200` |
| `SEARCH_OFFSET` | Default search offset | `0` |
| `HIERARCHYTYPE` | Boundary hierarchy type | `MICROPLAN` |
| `BOUNDARY_TYPE` | Boundary type | `LOCALITY` |
| `BOUNDARY_CODE` | Boundary code | `MICROPLAN_MO_13_03_02_03_02_TUGLOR` |
| `SERVICE_INDIVIDUAL` | Individual service name | `individual` |
| `SERVICE_PROJECT` | Project service name | `project` |
| `SERVICE_MDMS` | MDMS service name | `mdms-v2` |

### Pytest Configuration (pytest.ini)

```ini
[pytest]
pythonpath = .
```

This ensures the root directory is in the Python path for imports.

---

## Services Covered

| Service | Operations | Test File |
|---------|-----------|-----------|
| **Individual** | Create, Search | `test_individual_service.py` |
| **Household** | Create Household, Create Member, Search Household, Search Member | `test_household_service.py` |
| **Boundary** | Search with hierarchy | `test_boundary_service.py` |
| **Facility** | Create, Search | `test_facility_service.py` |
| **Product** | Create Product, Create Variant, Search Product, Search Variant | `test_product_service.py` |
| **Project** | Create, Search | `test_project_service.py` |
| **MDMS** | Search master data | `test_mdms_service.py` |

**Total: 7 Services, 16 Payload Templates**

---

## Writing Tests

### Test Structure

Each test module follows this pattern:

```python
# 1. Imports
from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info

# 2. Test Functions (with assertions)
def test_create_entity():
    """Test case with assertions"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    response = create_entity(token, client)

    # Assertions
    assert response.status_code in [200, 202], f"Failed: {response.text}"
    entity_id = response.json()["Entity"]["id"]
    assert entity_id, "Entity ID not generated"

    # Store ID for later use
    with open("output/ids.txt", "a") as f:
        f.write(f"Entity ID: {entity_id}\n")

# 3. Helper Functions (reusable, no assertions)
def create_entity(token, client):
    """Helper function for entity creation"""
    payload = load_payload("service_name", "create_entity.json")

    # Inject dynamic data
    payload["Entity"]["clientReferenceId"] = str(uuid.uuid4())
    payload["RequestInfo"] = get_request_info(token)

    return client.post("/service/v1/_create", payload)
```

### Key Principles

1. **Separation of Concerns**: Test functions contain assertions; helper functions contain reusable logic
2. **Token Reuse**: Obtain token once per test, reuse across operations
3. **Dynamic Data Injection**: Use UUID for unique identifiers, extract IDs from output files for dependencies
4. **Status Code Flexibility**: Accept both 200 (OK) and 202 (Accepted)
5. **Detailed Error Messages**: Include response text in assertion failures

### Adding a New Service

1. **Create Payload Directory**:
   ```bash
   mkdir payloads/new_service
   ```

2. **Add Payload Templates**:
   ```bash
   # Create JSON files for create, search operations
   touch payloads/new_service/create_entity.json
   touch payloads/new_service/search_entity.json
   ```

3. **Create Test File**:
   ```bash
   touch tests/test_new_service.py
   ```

4. **Implement Tests**:
   ```python
   from utils.api_client import APIClient
   from utils.auth import get_auth_token
   from utils.data_loader import load_payload
   from utils.request_info import get_request_info
   import uuid

   def test_create_new_entity():
       token = get_auth_token("user")
       client = APIClient(token=token)

       response = create_new_entity(token, client)
       assert response.status_code in [200, 202]

   def create_new_entity(token, client):
       payload = load_payload("new_service", "create_entity.json")
       payload["Entity"]["clientReferenceId"] = str(uuid.uuid4())
       payload["RequestInfo"] = get_request_info(token)
       return client.post("/new-service/v1/_create", payload)
   ```

---

## Running Tests

### Normal Execution

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_individual_service.py

# Run specific test function
pytest tests/test_individual_service.py::test_create_individual

# Run with verbose output
pytest tests/ -v

# Run with print statements visible
pytest tests/ -s
```

### HTML Report Generation

```bash
pytest tests/ --html=reports/report.html --self-contained-html
```

The HTML report will be generated at `reports/report.html` with:
- Test results summary
- Pass/Fail status
- Execution time
- Error details

### Allure Report Generation

```bash
# Generate Allure results
pytest --alluredir=allure-results

# Generate Allure report
allure generate allure-results --clean -o allure-report

# Open Allure report in browser
allure open allure-report
```

### Fresh Test Run (Clear Previous IDs)

```bash
echo "=== New Test Run ===" > output/ids.txt && pytest tests/ --html=reports/report.html --self-contained-html
```

This clears the `output/ids.txt` file before running tests, ensuring no stale IDs are used.

---

## Reporting

### Output Files

1. **output/ids.txt**
   - Stores entity IDs created during test execution
   - Format: `Entity Type ID: <id_value>`
   - Used by subsequent tests to reference created entities

2. **output/response.json**
   - Latest API response saved for inspection
   - Useful for debugging

3. **output/boundaries.txt**
   - Boundary hierarchy information from boundary service tests

### Report Types

1. **HTML Report** (`reports/report.html`)
   - Self-contained HTML file
   - Summary dashboard with pass/fail counts
   - Detailed test results with error traces

2. **Allure Report** (`allure-report/`)
   - Rich, interactive web-based report
   - Test execution trends
   - Test categorization and filtering
   - Detailed logs and attachments

---

## Utilities Documentation

### api_client.py

**Class: APIClient**

HTTP client wrapper with automatic authentication.

```python
from utils.api_client import APIClient

# Initialize with token
client = APIClient(token="your_token_here")

# Make requests
response = client.get("/endpoint")
response = client.post("/endpoint", payload)
response = client.put("/endpoint", payload)
response = client.delete("/endpoint")
```

**Constructor Parameters:**
- `service` (optional): Service name to fetch token for
- `token` (optional): Direct token value
- Must provide either `service` or `token`

**Methods:**
- `get(endpoint, params=None)`: GET request
- `post(endpoint, data=None)`: POST request
- `put(endpoint, data=None)`: PUT request
- `delete(endpoint)`: DELETE request

### auth.py

**Function: get_auth_token(service)**

Obtains OAuth2 access token for a service.

```python
from utils.auth import get_auth_token

token = get_auth_token("user")
```

**Parameters:**
- `service` (str): Service name (e.g., "user", "individual")

**Returns:**
- `str`: Access token

**Raises:**
- `Exception`: If authentication fails

### config.py

Configuration module with environment variables.

```python
from utils.config import BASE_URL, tenantId, search_params

# Use configuration values
url = BASE_URL
tenant = tenantId
params = search_params  # Contains limit, offset, tenantId
```

**Available Variables:**
- `BASE_URL`: API base URL
- `tenantId`: Tenant identifier
- `search_limit`, `search_offset`: Pagination settings
- `search_params`: Dictionary with limit, offset, tenantId
- `hierarchyType`, `boundaryCode`, `boundaryType`: Boundary configs
- `individual`, `project`, `mdms`: Service names

### data_loader.py

**Function: load_payload(service_name, filename)**

Loads JSON payload template.

```python
from utils.data_loader import load_payload

payload = load_payload("individual", "create_individual.json")
```

**Parameters:**
- `service_name` (str): Service folder name under `payloads/`
- `filename` (str): JSON file name

**Returns:**
- `dict`: Parsed JSON payload

### request_info.py

**Function: get_request_info(token)**

Creates standardized RequestInfo object.

```python
from utils.request_info import get_request_info

request_info = get_request_info(token)
payload["RequestInfo"] = request_info
```

**Parameters:**
- `token` (str): Authentication token

**Returns:**
- `dict`: RequestInfo object with API metadata, user context, and authentication

### search_helpers.py

**Function: search_entity(...)**

Generic search operation for entities.

```python
from utils.search_helpers import search_entity

results = search_entity(
    entity_type="Individual",
    token=token,
    client=client,
    entity_id="individual_id",
    payload_file="search_individual.json",
    endpoint="/individual/v1/_search",
    response_key="Individual"
)
```

**Parameters:**
- `entity_type` (str): Type of entity being searched
- `token` (str): Authentication token
- `client` (APIClient): API client instance
- `entity_id` (str): ID to search for
- `payload_file` (str): Payload file name
- `endpoint` (str): API endpoint
- `response_key` (str): Key in response containing results

**Function: extract_id_from_file(label)**

Extracts ID from output file.

```python
from utils.search_helpers import extract_id_from_file

individual_id = extract_id_from_file("Individual ID:")
```

**Parameters:**
- `label` (str): Label to search for in output/ids.txt

**Returns:**
- `str`: Extracted ID value

---

## Best Practices

### 1. Test Independence

- Each test should be independent and not rely on execution order
- Use output files for sharing data between tests that must run sequentially
- Clean up test data when possible

### 2. Error Handling

- Always include response text in assertion messages for debugging
- Use try-except blocks for critical operations
- Log errors to output files

### 3. Payload Management

- Keep payloads as templates with minimal hardcoded values
- Inject dynamic data (UUIDs, IDs) at runtime
- Reuse payloads across similar tests

### 4. Code Reusability

- Extract common operations into helper functions
- Use utility modules for shared functionality
- Follow DRY (Don't Repeat Yourself) principle

### 5. Documentation

- Add docstrings to test functions and helpers
- Comment complex logic
- Keep README updated with new services/features

### 6. Version Control

- Commit frequently with meaningful messages
- Use feature branches for new services
- Keep `.env` file out of version control (add to `.gitignore`)

---

## Git Workflow

### Working with Branches

```bash
# Check current branch
git status

# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Create new feature branch
git checkout -b feature/new-service

# Make changes and commit
git add .
git commit -m "Add new service tests"

# Push feature branch
git push origin feature/new-service
```

### Merging Branches

```bash
# Switch to main branch
git checkout main

# Pull latest main
git pull origin main

# Merge feature branch
git merge feature/new-service

# Push merged changes
git push origin main
```

### Merging Product Branch to Main

```bash
# Make sure you're on main
git checkout main

# Pull latest main branch from remote
git pull origin main

# Merge product branch into main
git merge product

# Push merged changes back to remote main
git push origin main
```

---

## Troubleshooting

### Common Issues

1. **Authentication Failure**
   - Verify `.env` credentials are correct
   - Check CLIENT_AUTH_HEADER is properly base64 encoded
   - Ensure token hasn't expired

2. **Import Errors**
   - Verify virtual environment is activated
   - Check `pytest.ini` has `pythonpath = .`
   - Install all required dependencies

3. **Test Failures**
   - Check API endpoint availability
   - Verify payload structure matches API requirements
   - Review `output/response.json` for error details

4. **Missing IDs**
   - Ensure prerequisite tests ran successfully
   - Check `output/ids.txt` has required IDs
   - Run tests in correct sequence

---

## Contributing

1. Create a feature branch
2. Make changes with clear commit messages
3. Add tests for new functionality
4. Update documentation
5. Create pull request

---

## License

[Add license information here]

---

## Contact

[Add contact information here]

---

**Last Updated**: 2025-10-27
