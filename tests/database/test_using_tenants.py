import unittest
import sys

sys.path.append(".")

import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import TenantDB
import tests.database.models as models
import tests._utils.api_test as api_test
from tests._utils.setup_utils import TenantFromTokenMock


TENANT_EMPTY = TenantFromTokenMock(current="")
TENANT_1 = TenantFromTokenMock(current="tenant_1")
TENANT_2 = TenantFromTokenMock(current="tenant_2")
NONEXISTENT_TENANT = TenantFromTokenMock(current="nonexistent-tenant")


class Test_Creating_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()

    def test_creating_object_with_empty_tenant_yields_401_error(self) -> None:
        obj = models.TestItem(test_str="test", test_int=4)
        response = _db_access.add(TENANT_EMPTY, obj)
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
        response = _db_access.add(TENANT_1, obj_1)
        assert response.status_code == 200, response.body
        _db_access.add(TENANT_2, obj_2)

    def test_retrieving_objects_with_empty_tenant_yields_all_objects(self) -> None:
        response = _db_access.get(tenants=TENANT_EMPTY, base=models.TestItem)
        self.assertEqual(response[0].test_str, "test1")
        self.assertEqual(response[1].test_str, "test2")

    def test_retrieving_objects_with_specified_existing_tenant_yields_objects_owned_by_tenant(
        self,
    ) -> None:
        response = _db_access.get(tenants=TENANT_1, base=models.TestItem)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].test_str, "test1")

        response = _db_access.get(tenants=TENANT_2, base=models.TestItem)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].test_str, "test2")

    def test_retrieving_objects_with_nonexistent_tenant_yields_empty_list(self) -> None:
        response = _db_access.get(tenants=NONEXISTENT_TENANT, base=models.TestItem)
        self.assertEqual(response, [])


class Test_Updating_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(TenantDB(name="tenant_1"), TenantDB(name="tenant_2"))
        obj_1 = models.TestItem(test_str="test1", test_int=4)
        obj_2 = models.TestItem(test_str="test2", test_int=4)
        _db_access.add(TENANT_1, obj_1)
        _db_access.add(TENANT_2, obj_2)

    def test_updating_objects_with_empty_tenant_yields_400_error(self) -> None:
        obj = models.TestItem(id=1, test_str="test1", test_int=4)
        response = _db_access.update(TENANT_EMPTY, obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_updating_objects_with_nonexistent_tenant_yields_404_error(self) -> None:
        obj = models.TestItem(id=1, test_str="test1", test_int=4)
        response = _db_access.update(NONEXISTENT_TENANT, obj)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["title"], "Tenant not found.")

    def test_updating_objects_with_existing_tenant_specified_is_accepted(self) -> None:
        obj = models.TestItem(id=1, test_str="test1", test_int=8)
        response = _db_access.update(TENANT_1, obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body[0].test_int, 8)


class Test_Deleting_Objects(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(TenantDB(name="tenant_1"), TenantDB(name="tenant_2"))
        obj_1 = models.TestItem(test_str="test1", test_int=4)
        _db_access.add(TENANT_1, obj_1)

    def test_deleting_objects_with_empty_tenant_yields_400_error(self) -> None:
        response = _db_access.delete(TENANT_EMPTY, base=models.TestItem, id_=1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["title"], "Tenant not received.")

    def test_deleting_objects_with_nonexistent_tenant_yields_404_error(self) -> None:
        response = _db_access.delete(NONEXISTENT_TENANT, models.TestItem, id_=1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["title"], "Tenant not found.")

    def test_deleting_objects_with_existing_tenant_specified_is_accepted(self) -> None:
        response = _db_access.delete(TENANT_1, models.TestItem, id_=1)
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

    def test_tenant_owning_some_object_cannot_be_deleted_and_yields_400_error(self) -> None:
        obj = models.TestItem(test_str="test1", test_int=4)
        _db_access.add(TENANT_1, obj)
        response = _db_access.delete_without_tenant(TenantDB, id_=1)
        self.assertEqual(response.status_code, 400)
        print(response.body)


if __name__ == "__main__":
    unittest.main(verbosity=2)  # pragma: no cover
