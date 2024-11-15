import unittest
import sys

sys.path.append(".")

import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import TenantDBModel
import tests.database.models as models
import tests._utils.api_test as api_test


class Test_Creating_Objects(api_test.TestCase):

    def test_creating_object_with_empty_tenant_yields_400_error(self) -> None:
        obj = models.TestBase(test_str="test", test_int=4)
        response = _db_access.add("", obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_creating_object_with_nonexistent_tenant_yields_404_error(self) -> None:
        obj = models.TestBase(test_str="test", test_int=4)
        response = _db_access.add("nonexistent-tenant", obj)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["title"], "Tenant not found.")

    def test_creating_object_with_existing_tenant_specified_is_accepted(self) -> None:
        obj = models.TestBase(test_str="test", test_int=4)
        _db_access.add_without_tenant(TenantDBModel(name="test-tenant"))
        response = _db_access.add("test-tenant", obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, [obj])


class Test_Retrieving_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(
            TenantDBModel(name="tenant_1"), TenantDBModel(name="tenant_2")
        )
        obj_1 = models.TestBase(test_str="test1", test_int=4)
        obj_2 = models.TestBase(test_str="test2", test_int=4)
        _db_access.add("tenant_1", obj_1)
        _db_access.add("tenant_2", obj_2)

    def test_retrieving_objects_with_empty_tenant_yields_all_objects(self) -> None:
        response = _db_access.get(base=models.TestBase)
        self.assertEqual(response[0].test_str, "test1")
        self.assertEqual(response[1].test_str, "test2")

    def test_retrieving_objects_with_specified_existing_tenant_yields_objects_owned_by_tenant(
        self,
    ) -> None:
        response = _db_access.get(tenant="tenant_1", base=models.TestBase)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].test_str, "test1")

        response = _db_access.get(tenant="tenant_2", base=models.TestBase)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].test_str, "test2")

    def test_retrieving_objects_with_nonexistent_tenant_yields_empty_list(self) -> None:
        response = _db_access.get(tenant="nonexistent-tenant", base=models.TestBase)
        self.assertEqual(response, [])


class Test_Updating_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(
            TenantDBModel(name="tenant_1"), TenantDBModel(name="tenant_2")
        )
        obj_1 = models.TestBase(test_str="test1", test_int=4)
        obj_2 = models.TestBase(test_str="test2", test_int=4)
        _db_access.add("tenant_1", obj_1)
        _db_access.add("tenant_2", obj_2)

    def test_updating_objects_with_empty_tenant_yields_400_error(self) -> None:
        obj = models.TestBase(id=1, test_str="test1", test_int=4)
        response = _db_access.update("", obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_updating_objects_with_nonexistent_tenant_yields_404_error(self) -> None:
        obj = models.TestBase(id=1, test_str="test1", test_int=4)
        response = _db_access.update("nonexistent-tenant", obj)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["title"], "Tenant not found.")

    def test_updating_objects_with_existing_tenant_specified_is_accepted(self) -> None:
        obj = models.TestBase(id=1, test_str="test1", test_int=8)
        response = _db_access.update("tenant_1", obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body[0].test_int, 8)


class Test_Deleting_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(
            TenantDBModel(name="tenant_1"), TenantDBModel(name="tenant_2")
        )
        obj_1 = models.TestBase(test_str="test1", test_int=4)
        _db_access.add("tenant_1", obj_1)

    def test_deleting_objects_with_empty_tenant_yields_400_error(self) -> None:
        response = _db_access.delete(tenant="", base=models.TestBase, id_=1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_deleting_objects_with_nonexistent_tenant_yields_404_error(self) -> None:
        response = _db_access.delete("nonexistent-tenant", models.TestBase, id_=1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["title"], "Tenant not found.")

    def test_deleting_objects_with_existing_tenant_specified_is_accepted(self) -> None:
        response = _db_access.delete("tenant_1", models.TestBase, id_=1)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)  # pragma: no cover
