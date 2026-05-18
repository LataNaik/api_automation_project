"""
Entity Factory - Centralized entity creation for API tests.

This module provides factory functions for creating test entities.
It reduces code duplication by centralizing entity creation logic.
"""
import uuid
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import boundaryCode, tenantId, hierarchyType, boundaryCodeRoot


class EntityFactory:
    """
    Factory class for creating test entities.
    Provides a centralized way to create entities with consistent patterns.
    """

    def __init__(self, token, client):
        """
        Initialize the entity factory.

        Args:
            token: Authentication token
            client: APIClient instance
        """
        self.token = token
        self.client = client

    def _create_payload(self, entity_type, payload_file):
        """Load payload and add request info."""
        payload = load_payload(entity_type, payload_file)
        payload["RequestInfo"] = get_request_info(self.token)
        return payload

    def _post_and_extract(self, endpoint, payload, response_key, is_array=False):
        """
        Post request and extract entity data from response.

        Returns:
            Tuple of (entity_data, status_code) or (response) for errors
        """
        response = self.client.post(endpoint, payload)

        if response.status_code not in [200, 202]:
            return response

        entity_data = response.json()[response_key]
        if is_array and isinstance(entity_data, list):
            entity_data = entity_data[0]

        return entity_data, response.status_code

    # ==================== Individual ====================

    def create_individual(self, tenant_id=None):
        """
        Create an individual entity.

        Args:
            tenant_id: Override tenant ID (for negative testing)

        Returns:
            For success: (individual_id, client_ref_id, individual_ind_id, status_code)
            For negative tests: response object
        """
        payload = self._create_payload("individual", "create_individual.json")

        # Inject dynamic values
        payload["Individual"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Individual"]["address"][0]["clientReferenceId"] = str(uuid.uuid4())
        payload["Individual"]["address"][0]["locality"]["code"] = boundaryCode
        payload["Individual"]["identifiers"][0]["clientReferenceId"] = str(uuid.uuid4())
        payload["Individual"]["skills"][0]["clientReferenceId"] = str(uuid.uuid4())

        if tenant_id is not None:
            payload["Individual"]["tenantId"] = tenant_id
            payload["Individual"]["address"][0]["tenantId"] = tenant_id
            return self.client.post("/individual/v1/_create", payload)

        response = self.client.post("/individual/v1/_create", payload)

        if response.status_code not in [200, 202]:
            raise Exception(f"Individual creation failed: {response.text}")

        data = response.json()["Individual"]
        return data["id"], data["clientReferenceId"], data["individualId"], response.status_code

    def create_individual_full(self):
        """Create individual and return full data for update/delete."""
        payload = self._create_payload("individual", "create_individual.json")

        payload["Individual"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Individual"]["address"][0]["clientReferenceId"] = str(uuid.uuid4())
        payload["Individual"]["address"][0]["locality"]["code"] = boundaryCode
        payload["Individual"]["identifiers"][0]["clientReferenceId"] = str(uuid.uuid4())
        payload["Individual"]["skills"][0]["clientReferenceId"] = str(uuid.uuid4())

        response = self.client.post("/individual/v1/_create", payload)

        if response.status_code not in [200, 202]:
            raise Exception(f"Individual creation failed: {response.text}")

        return response.json()["Individual"], response.status_code

    # ==================== Facility ====================

    def create_facility(self, tenant_id=None):
        """
        Create a facility entity.

        Args:
            tenant_id: Override tenant ID (for negative testing)

        Returns:
            Response object
        """
        payload = self._create_payload("facility", "create_facility.json")
        payload["Facility"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Facility"]["address"]["locality"]["code"] = boundaryCode

        if tenant_id is not None:
            payload["Facility"]["tenantId"] = tenant_id

        return self.client.post("/facility/v1/_create", payload)

    def create_facility_full(self):
        """Create facility and return full data for update/delete."""
        payload = self._create_payload("facility", "create_facility.json")
        payload["Facility"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Facility"]["address"]["locality"]["code"] = boundaryCode

        response = self.client.post("/facility/v1/_create", payload)

        if response.status_code not in [200, 202]:
            raise Exception(f"Facility creation failed: {response.text}")

        return response.json()["Facility"], response.status_code

    # ==================== Household ====================

    def create_household(self, tenant_id=None):
        """
        Create a household entity.

        Args:
            tenant_id: Override tenant ID (for negative testing)

        Returns:
            For success: (household_id, client_ref_id, status_code)
            For negative tests: response object
        """
        payload = self._create_payload("household", "create_household.json")
        payload["Household"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Household"]["address"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Household"]["address"]["locality"]["code"] = boundaryCode

        if tenant_id is not None:
            payload["Household"]["tenantId"] = tenant_id
            payload["Household"]["address"]["tenantId"] = tenant_id
            return self.client.post("/household/v1/_create", payload)

        response = self.client.post("/household/v1/_create", payload)

        if response.status_code not in [200, 202]:
            raise Exception(f"Household creation failed: {response.text}")

        data = response.json()["Household"]
        return data["id"], data["clientReferenceId"], response.status_code

    def create_household_full(self):
        """Create household and return full data for update/delete."""
        payload = self._create_payload("household", "create_household.json")
        payload["Household"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Household"]["address"]["clientReferenceId"] = str(uuid.uuid4())
        payload["Household"]["address"]["locality"]["code"] = boundaryCode

        response = self.client.post("/household/v1/_create", payload)

        if response.status_code not in [200, 202]:
            raise Exception(f"Household creation failed: {response.text}")

        return response.json()["Household"], response.status_code

    # ==================== Product ====================

    def create_product(self, tenant_id=None):
        """
        Create a product entity.

        Returns:
            Response object
        """
        payload = self._create_payload("product", "create_product.json")

        if tenant_id is not None:
            payload["Product"][0]["tenantId"] = tenant_id

        return self.client.post("/product/v1/_create", payload)

    def create_product_full(self):
        """Create product and return full data for update/delete."""
        payload = self._create_payload("product", "create_product.json")

        response = self.client.post("/product/v1/_create", payload)

        if response.status_code not in [200, 202]:
            raise Exception(f"Product creation failed: {response.text}")

        return response.json()["Product"][0], response.status_code

    def create_product_variant(self, product_id=None, tenant_id=None):
        """
        Create a product variant entity.

        Args:
            product_id: Product ID to link to (creates new product if None or "create")
            tenant_id: Override tenant ID (for negative testing)

        Returns:
            Response object
        """
        # Create product if needed
        if product_id is None or product_id == "create":
            product_res = self.create_product()
            if product_res.status_code not in [200, 202]:
                raise Exception(f"Product creation for variant failed: {product_res.text}")
            product_id = product_res.json()["Product"][0]["id"]

        payload = self._create_payload("product", "create_productVariant.json")
        payload["ProductVariant"][0]["productId"] = product_id

        if tenant_id is not None:
            payload["ProductVariant"][0]["tenantId"] = tenant_id

        return self.client.post("/product/variant/v1/_create", payload)

    def create_product_variant_full(self):
        """Create product variant and return full data for update/delete."""
        product_res = self.create_product()
        if product_res.status_code not in [200, 202]:
            raise Exception(f"Product creation for variant failed: {product_res.text}")
        product_id = product_res.json()["Product"][0]["id"]

        payload = self._create_payload("product", "create_productVariant.json")
        payload["ProductVariant"][0]["productId"] = product_id

        response = self.client.post("/product/variant/v1/_create", payload)

        if response.status_code not in [200, 202]:
            raise Exception(f"Product Variant creation failed: {response.text}")

        return response.json()["ProductVariant"][0], response.status_code


def get_factory(token, client):
    """
    Get an EntityFactory instance.

    Args:
        token: Authentication token
        client: APIClient instance

    Returns:
        EntityFactory instance
    """
    return EntityFactory(token, client)
