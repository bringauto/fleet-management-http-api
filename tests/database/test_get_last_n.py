import unittest

import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
import tests.database.models as models
import tests._utils.api_test as api_test
from tests._utils.constants import TEST_TENANT_NAME
from tests._utils.setup_utils import TenantFromTokenMock


class Test_Retrieving_Last_N_Records(api_test.TestCase):

    def setUp(self):
        super().setUp()
        _db_access.add_without_tenant(_db_models.TenantDB(name=TEST_TENANT_NAME))
        self.tenant = TenantFromTokenMock(TEST_TENANT_NAME)

    def test_retrieving_single_item_with_highest_attribute_value(self):
        test_obj_1 = models.TestItem(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestItem(id=8, test_str="test_string", test_int=100)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get(
            self.tenant, models.TestItem, first_n=1, sort_result_by={"test_int": "desc"}
        )
        self.assertEqual(len(retrieved_objs), 1)
        self.assertEqual(retrieved_objs[0].test_int, 150)

    def test_retrieving_both_items_sorted_by_attribute_value_in_descending_order(self):
        test_obj_1 = models.TestItem(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestItem(id=8, test_str="test_string", test_int=100)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)
        retrieved_objs: list[models.TestItem] = _db_access.get(
            self.tenant, models.TestItem, first_n=2, sort_result_by={"test_int": "desc"}
        )
        self.assertEqual(retrieved_objs[0].test_int, 150)
        self.assertEqual(retrieved_objs[1].test_int, 100)

    def test_retrieving_the_two_items_with_highest_attribute_value(self):
        test_obj_1 = models.TestItem(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestItem(id=8, test_str="test_string", test_int=100)
        test_obj_3 = models.TestItem(id=9, test_str="test_string", test_int=120)
        _db_access.add(self.tenant, test_obj_1, test_obj_2, test_obj_3)
        retrieved_objs: list[models.TestItem] = _db_access.get(
            self.tenant, models.TestItem, first_n=2, sort_result_by={"test_int": "desc"}
        )
        self.assertEqual(len(retrieved_objs), 2)
        self.assertEqual(retrieved_objs[0].test_int, 150)
        self.assertEqual(retrieved_objs[1].test_int, 120)

    def test_retrieving_the_two_items_with_lowest_attribute_value(self):
        test_obj_1 = models.TestItem(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestItem(id=8, test_str="test_string", test_int=100)
        test_obj_3 = models.TestItem(id=9, test_str="test_string", test_int=120)
        _db_access.add(self.tenant, test_obj_1, test_obj_2, test_obj_3)
        retrieved_objs: list[models.TestItem] = _db_access.get(
            self.tenant, models.TestItem, first_n=3, sort_result_by={"test_int": "asc"}
        )
        self.assertEqual(retrieved_objs[0].test_int, 100)
        self.assertEqual(retrieved_objs[1].test_int, 120)

    def test_returning_items_with_highest_value_of_a_second_attribute_if_first_attribute_values_are_equal(
        self,
    ):
        test_obj_1 = models.TestItem(test_str="test_string", test_int=100)
        test_obj_2 = models.TestItem(test_str="test_string", test_int=100)
        test_obj_3 = models.TestItem(test_str="test_string", test_int=120)
        _db_access.add(self.tenant, test_obj_1, test_obj_2, test_obj_3)
        retrieved_objs: list[models.TestItem] = _db_access.get(
            self.tenant,
            models.TestItem,
            first_n=2,
            sort_result_by={"test_int": "desc", "id": "desc"},
        )
        self.assertEqual(retrieved_objs[0].test_int, 120)
        self.assertEqual(retrieved_objs[0].id, 3)
        self.assertEqual(retrieved_objs[1].test_int, 100)
        self.assertEqual(retrieved_objs[1].id, 2)

    def test_returning_items_with_lowest_value_of_a_second_attribute_if_first_attribute_values_are_equal(
        self,
    ):
        test_obj_1 = models.TestItem(test_str="test_string", test_int=100)
        test_obj_2 = models.TestItem(test_str="test_string", test_int=100)
        test_obj_3 = models.TestItem(test_str="test_string", test_int=120)
        _db_access.add(self.tenant, test_obj_1, test_obj_2, test_obj_3)
        retrieved_objs: list[models.TestItem] = _db_access.get(
            self.tenant,
            models.TestItem,
            first_n=2,
            sort_result_by={"test_int": "desc", "id": "asc"},
        )
        self.assertEqual(retrieved_objs[0].test_int, 120)
        self.assertEqual(retrieved_objs[0].id, 3)
        self.assertEqual(retrieved_objs[1].test_int, 100)
        self.assertEqual(retrieved_objs[1].id, 1)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
