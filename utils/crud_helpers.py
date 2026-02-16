"""
Shared CRUD helper functions for API automation tests.
These functions provide reusable patterns for create, search, update, and delete operations.
"""
import uuid
import os
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import search_params, tenantId


def write_to_ids_file(section_header, **kwargs):
    """
    Write entity IDs to the output/ids.txt file.

    Args:
        section_header: Header for the section (e.g., "Facility details")
        **kwargs: Key-value pairs to write (e.g., facility_id="123")

    Example:
        write_to_ids_file("Facility details",
                         facility_id="abc123",
                         client_ref_id="xyz789")
    """
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    ids_file = os.path.join(output_dir, "ids.txt")

    with open(ids_file, "a") as f:
        f.write(f"\n--- {section_header} ---\n")
        for key, value in kwargs.items():
            # Convert snake_case to Title Case for display
            display_key = key.replace("_", " ").title()
            f.write(f"{display_key}: {value}\n")


def generate_client_reference_id():
    """Generate a unique client reference ID using UUID."""
    return str(uuid.uuid4())


def create_entity(client, token, entity_type, payload_file, endpoint,
                  entity_key, response_key=None, payload_modifier=None,
                  return_full_response=False):
    """
    Generic function to create an entity.

    Args:
        client: APIClient instance
        token: Auth token
        entity_type: Entity type for payload loading (e.g., "facility")
        payload_file: Payload JSON filename (e.g., "create_facility.json")
        endpoint: API endpoint (e.g., "/facility/v1/_create")
        entity_key: Key in payload for the entity (e.g., "Facility")
        response_key: Key in response for entity data (defaults to entity_key)
        payload_modifier: Optional function to modify payload before sending
        return_full_response: If True, returns (entity_data, status_code), else returns response

    Returns:
        If return_full_response=True: Tuple of (entity_data, status_code)
        Else: Response object
    """
    payload = load_payload(entity_type, payload_file)
    payload["RequestInfo"] = get_request_info(token)

    # Apply payload modifications if provided
    if payload_modifier:
        payload = payload_modifier(payload)

    response = client.post(endpoint, payload)

    if return_full_response:
        if response.status_code not in [200, 202]:
            raise Exception(f"{entity_key} creation failed with status {response.status_code}: {response.text}")

        resp_key = response_key or entity_key
        entity_data = response.json()[resp_key]

        # Handle array responses (like Product returns [{}])
        if isinstance(entity_data, list):
            entity_data = entity_data[0]

        return entity_data, response.status_code

    return response


def search_entity_by_id(client, token, entity_type, payload_file, endpoint,
                        entity_id, entity_key, response_key):
    """
    Generic function to search for an entity by ID.

    Args:
        client: APIClient instance
        token: Auth token
        entity_type: Entity type for payload loading
        payload_file: Payload JSON filename
        endpoint: API endpoint
        entity_id: ID to search for
        entity_key: Key in payload for the entity
        response_key: Key in response containing results

    Returns:
        List of matching entities
    """
    payload = load_payload(entity_type, payload_file)
    payload["RequestInfo"] = get_request_info(token)

    # Handle different payload structures
    if isinstance(payload[entity_key], list):
        payload[entity_key][0]["id"] = entity_id
    else:
        payload[entity_key]["id"] = [entity_id]

    query_string = "&".join(f"{k}={v}" for k, v in search_params.items())
    url = f"{endpoint}?{query_string}"

    response = client.post(url, payload)
    assert response.status_code == 200, f"Search failed: {response.text}"

    return response.json().get(response_key, [])


def update_entity(client, token, entity_type, payload_file, endpoint,
                  entity_key, entity_data, updates, response_key=None):
    """
    Generic function to update an entity.

    Args:
        client: APIClient instance
        token: Auth token
        entity_type: Entity type for payload loading
        payload_file: Payload JSON filename
        endpoint: API endpoint
        entity_key: Key in payload for the entity
        entity_data: Full entity data from create/search
        updates: Dict of fields to update
        response_key: Key in response (defaults to entity_key)

    Returns:
        Response object
    """
    payload = load_payload(entity_type, payload_file)
    payload["RequestInfo"] = get_request_info(token)

    # Determine if payload uses array or object structure
    if isinstance(payload[entity_key], list):
        target = payload[entity_key][0]
    else:
        target = payload[entity_key]

    # Copy required fields from entity_data
    required_fields = ["id", "tenantId", "rowVersion", "auditDetails"]
    for field in required_fields:
        if field in entity_data:
            target[field] = entity_data[field]

    # Copy optional fields
    optional_fields = ["clientReferenceId", "clientAuditDetails"]
    for field in optional_fields:
        if field in entity_data:
            target[field] = entity_data.get(field)

    # Apply updates
    for key, value in updates.items():
        target[key] = value

    response = client.post(endpoint, payload)
    return response


def delete_entity(client, token, entity_type, payload_file, endpoint,
                  entity_key, entity_data, response_key=None):
    """
    Generic function to soft-delete an entity (set isDeleted=true).

    Args:
        client: APIClient instance
        token: Auth token
        entity_type: Entity type for payload loading
        payload_file: Payload JSON filename
        endpoint: API endpoint
        entity_key: Key in payload for the entity
        entity_data: Full entity data from create/search
        response_key: Key in response (defaults to entity_key)

    Returns:
        Response object
    """
    payload = load_payload(entity_type, payload_file)
    payload["RequestInfo"] = get_request_info(token)

    # Determine if payload uses array or object structure
    if isinstance(payload[entity_key], list):
        target = payload[entity_key][0]
    else:
        target = payload[entity_key]

    # Copy all fields from entity_data
    for key, value in entity_data.items():
        if key not in ["isDeleted"]:  # Don't copy isDeleted from original
            target[key] = value

    # Set isDeleted flag
    target["isDeleted"] = True

    response = client.post(endpoint, payload)
    return response


def test_create_with_invalid_tenant(client, token, entity_type, payload_file,
                                     endpoint, entity_key, invalid_tenant_id,
                                     payload_modifier=None):
    """
    Generic negative test for creating entity with invalid tenant ID.

    Args:
        client: APIClient instance
        token: Auth token
        entity_type: Entity type for payload loading
        payload_file: Payload JSON filename
        endpoint: API endpoint
        entity_key: Key in payload for the entity
        invalid_tenant_id: Invalid tenant ID to use
        payload_modifier: Optional function to modify payload

    Returns:
        Response object
    """
    payload = load_payload(entity_type, payload_file)
    payload["RequestInfo"] = get_request_info(token)

    # Apply payload modifications if provided
    if payload_modifier:
        payload = payload_modifier(payload)

    # Set invalid tenant ID
    if isinstance(payload[entity_key], list):
        payload[entity_key][0]["tenantId"] = invalid_tenant_id
    else:
        payload[entity_key]["tenantId"] = invalid_tenant_id

    response = client.post(endpoint, payload)
    return response


def test_search_with_invalid_tenant(client, token, entity_type, payload_file,
                                     endpoint, entity_key, entity_id,
                                     invalid_tenant_id):
    """
    Generic negative test for searching entity with invalid tenant ID.

    Args:
        client: APIClient instance
        token: Auth token
        entity_type: Entity type for payload loading
        payload_file: Payload JSON filename
        endpoint: API endpoint (without query params)
        entity_key: Key in payload for the entity
        entity_id: ID to search for
        invalid_tenant_id: Invalid tenant ID to use

    Returns:
        Response object
    """
    payload = load_payload(entity_type, payload_file)
    payload["RequestInfo"] = get_request_info(token)

    # Set the entity ID in payload
    if isinstance(payload[entity_key], list):
        payload[entity_key][0]["id"] = entity_id
    else:
        payload[entity_key]["id"] = [entity_id]

    url = f"{endpoint}?tenantId={invalid_tenant_id}"
    response = client.post(url, payload)
    return response


def copy_entity_fields(target, source, fields):
    """
    Copy specified fields from source dict to target dict.

    Args:
        target: Target dictionary to copy to
        source: Source dictionary to copy from
        fields: List of field names to copy
    """
    for field in fields:
        if field in source:
            target[field] = source[field]


def copy_entity_fields_with_get(target, source, fields, defaults=None):
    """
    Copy specified fields from source dict to target dict using .get() for optional fields.

    Args:
        target: Target dictionary to copy to
        source: Source dictionary to copy from
        fields: List of field names to copy
        defaults: Optional dict of default values for fields
    """
    defaults = defaults or {}
    for field in fields:
        default_value = defaults.get(field)
        target[field] = source.get(field, default_value)


# Entity-specific helper functions that use the generic functions

def assert_create_success(response, entity_name="Entity"):
    """Assert that a create operation succeeded."""
    assert response.status_code in [200, 202], f"{entity_name} creation failed: {response.text}"


def assert_search_found(entities, entity_id, entity_name="Entity"):
    """Assert that an entity was found in search results."""
    ids = [e["id"] for e in entities]
    assert entity_id in ids, f"{entity_name} not found"


def assert_update_success(response, entity_name="Entity"):
    """Assert that an update operation succeeded."""
    assert response.status_code in [200, 202], f"{entity_name} update failed: {response.text}"


def assert_delete_success(response, entity_data, entity_key, entity_name="Entity"):
    """Assert that a delete operation succeeded and entity is marked as deleted."""
    assert response.status_code in [200, 202], f"{entity_name} delete failed: {response.text}"
    deleted_entity = response.json()[entity_key]
    if isinstance(deleted_entity, list):
        deleted_entity = deleted_entity[0]
    assert deleted_entity.get("isDeleted") == True, f"{entity_name} not marked as deleted"


def assert_negative_test_failed(response, expected_codes=None, test_name="Negative test"):
    """Assert that a negative test returned expected error status."""
    expected_codes = expected_codes or [400, 401, 403]
    assert response.status_code in expected_codes, \
        f"{test_name}: Expected one of {expected_codes}, got {response.status_code}: {response.text}"
