import unittest
import sys
import jwt

sys.path.append(".")

from connexion.lifecycle import ConnexionRequest

import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import TenantDB
from fleet_management_api.api_impl.security import TenantFromToken
import tests.database.models as models
import tests._utils.api_test as api_test


TENANT_FROM_EMPTY_TOKEN = TenantFromToken(
    ConnexionRequest("http://example.com", method="GET"), key=""
)
token = jwt.encode(
    {"Payload": '{"group": ["/customers/tenant_1", "/customers/tenant_2"]}'},
    "test_key",
    algorithm="HS256",
)
TENANT_EMPTY = TenantFromToken(
    ConnexionRequest(
        "http://example.com", method="GET", headers={"Authorization": f"Bearer {token}"}
    ),
    key="test_key",
)
TENANT_1 = TenantFromToken(
    ConnexionRequest(
        "http://example.com",
        method="GET",
        cookies={"tenant": "tenant_1"},
        headers={"Authorization": f"Bearer {token}"},
    ),
    key="test_key",
)
TENANT_2 = TenantFromToken(
    ConnexionRequest(
        "http://example.com",
        method="GET",
        cookies={"tenant": "tenant_2"},
        headers={"Authorization": f"Bearer {token}"},
    ),
    key="test_key",
)


class Test_Creating_Objects(api_test.TestCase):

    def test_creating_object_with_empty_tenant_yields_401_error(self) -> None:
        obj = models.TestItem(test_str="test", test_int=4)
        response = _db_access.add(TENANT_FROM_EMPTY_TOKEN, obj)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_creating_object_with_existing_tenant_specified_is_accepted(self) -> None:
        obj = models.TestItem(test_str="test", test_int=4)
        _db_access.add_without_tenant(TenantDB(name="tenant_1"))
        response = _db_access.add(TENANT_1, obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body[0].id, obj.id)
        self.assertEqual(response.body[0].test_str, obj.test_str)
        self.assertEqual(response.body[0].test_int, obj.test_int)


class Test_Retrieving_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(TenantDB(name="tenant_1"), TenantDB(name="tenant_2"))
        obj_1 = models.TestItem(test_str="test1", test_int=4)
        obj_2 = models.TestItem(test_str="test2", test_int=4)
        _db_access.add(TENANT_1, obj_1)
        _db_access.add(TENANT_2, obj_2)

    def test_retrieving_objects_with_empty_tenant_yields_all_objects(self) -> None:
        response = _db_access.get(tenant=TENANT_EMPTY, base=models.TestItem)
        self.assertEqual(response[0].test_str, "test1")
        self.assertEqual(response[1].test_str, "test2")

    def test_retrieving_objects_with_specified_existing_tenant_yields_objects_owned_by_tenant(
        self,
    ) -> None:
        response = _db_access.get(tenant=TENANT_1, base=models.TestItem)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].test_str, "test1")

        response = _db_access.get(tenant="tenant_2", base=models.TestItem)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].test_str, "test2")

    def test_retrieving_objects_with_nonexistent_tenant_yields_empty_list(self) -> None:
        response = _db_access.get(tenant="nonexistent-tenant", base=models.TestItem)
        self.assertEqual(response, [])


class Test_Updating_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(TenantDB(name="tenant_1"), TenantDB(name="tenant_2"))
        obj_1 = models.TestItem(test_str="test1", test_int=4)
        obj_2 = models.TestItem(test_str="test2", test_int=4)
        _db_access.add("tenant_1", obj_1)
        _db_access.add("tenant_2", obj_2)

    def test_updating_objects_with_empty_tenant_yields_400_error(self) -> None:
        obj = models.TestItem(id=1, test_str="test1", test_int=4)
        response = _db_access.update("", obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_updating_objects_with_nonexistent_tenant_yields_404_error(self) -> None:
        obj = models.TestItem(id=1, test_str="test1", test_int=4)
        response = _db_access.update("nonexistent-tenant", obj)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["title"], "Tenant not found.")

    def test_updating_objects_with_existing_tenant_specified_is_accepted(self) -> None:
        obj = models.TestItem(id=1, test_str="test1", test_int=8)
        response = _db_access.update("tenant_1", obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body[0].test_int, 8)


class Test_Deleting_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(TenantDB(name="tenant_1"), TenantDB(name="tenant_2"))
        obj_1 = models.TestItem(test_str="test1", test_int=4)
        _db_access.add("tenant_1", obj_1)

    def test_deleting_objects_with_empty_tenant_yields_400_error(self) -> None:
        response = _db_access.delete(tenant="", base=models.TestItem, id_=1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_deleting_objects_with_nonexistent_tenant_yields_404_error(self) -> None:
        response = _db_access.delete("nonexistent-tenant", models.TestItem, id_=1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["title"], "Tenant not found.")

    def test_deleting_objects_with_existing_tenant_specified_is_accepted(self) -> None:
        response = _db_access.delete("tenant_1", models.TestItem, id_=1)
        self.assertEqual(response.status_code, 200)


class Test_Deleting_Tenants(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(TenantDB(name="tenant_1"))

    def test_deleting_existing_tenant_is_accepted(self) -> None:
        response = _db_access.delete_without_tenant(TenantDB, id_=1)
        self.assertEqual(response.status_code, 200)

    def test_deleting_nonexisting_tenant_is_yields_404_error(self) -> None:
        response = _db_access.delete_without_tenant(TenantDB, id_=2)
        self.assertEqual(response.status_code, 404)

    def _test_tenant_owning_some_object_cannot_be_deleted_and_yields_400_error(self) -> None:
        obj = models.TestItem(test_str="test1", test_int=4)
        _db_access.add("tenant_1", obj)
        response = _db_access.delete_without_tenant(TenantDB, id_=1)
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)  # pragma: no cover
