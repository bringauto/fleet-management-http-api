import unittest

import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import TenantDB
import tests.database.models as models
import tests._utils.api_test as api_test
from tests._utils.setup_utils import TenantFromTokenMock
from tests._utils.constants import TEST_TENANT_NAME


def _set_up_test_data():
    _db_access.add_without_tenant(TenantDB(name=TEST_TENANT_NAME))


class Test_Creating_Records(api_test.TestCase):

    def setUp(self, *args, test_db_path: str = "", **kwargs) -> None:
        super().setUp(test_db_path)
        _set_up_test_data()
        self.tenant = TenantFromTokenMock(TEST_TENANT_NAME)

    def test_adding_single_record_to_database_succesfully(self):
        test_obj = models.TestItem(test_str="test_string", test_int=5)
        _db_access.add(self.tenant, test_obj)
        retrieved_obj = _db_access.get(tenants=self.tenant, base=models.TestItem)[0]
        self.assertEqual(retrieved_obj.test_str, test_obj.test_str)
        self.assertEqual(retrieved_obj.test_int, test_obj.test_int)

    def test_adding_multiple_records_to_database_succesfully(self):
        test_obj_1 = models.TestItem(test_str="test_string", test_int=5)
        test_obj_2 = models.TestItem(test_str="test_string", test_int=8)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertEqual(retrieved_objs[0].test_int, test_obj_1.test_int)
        self.assertEqual(retrieved_objs[1].test_int, test_obj_2.test_int)

    def test_single_failure_prevents_all_records_from_uploading_to_database(self):
        # failure is produced by the third record, having already taken ID
        test_obj_1 = models.TestItem(test_str="test_string", test_int=5, id=0)
        test_obj_2 = models.TestItem(test_str="test_string", test_int=8, id=1)
        test_obj_3 = models.TestItem(test_str="test_string", test_int=9, id=1)
        response = _db_access.add(self.tenant, test_obj_1, test_obj_2, test_obj_3, auto_id=False)
        self.assertEqual(response.status_code, 400)
        records = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertListEqual(records, [])


class Test_Sending_And_Retrieving_From_Database(api_test.TestCase):

    def setUp(self, *args, test_db_path: str = "", **kwargs) -> None:
        super().setUp(test_db_path)
        _set_up_test_data()
        self.tenant = TenantFromTokenMock(TEST_TENANT_NAME)

    def test_table_is_initially_empty(self):
        objs_out = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertListEqual(objs_out, [])

    def test_data_retrieved_are_equal_to_data_sent(self):
        data_in = models.TestItem(test_str="test_string", test_int=5)
        _db_access.add(self.tenant, data_in)
        data_out: models.TestItem = _db_access.get(tenants=self.tenant, base=models.TestItem)[0]
        self.assertEqual(data_out.id, 1)
        self.assertEqual(data_out.test_str, data_in.test_str)
        self.assertEqual(data_out.test_int, data_in.test_int)

    def test_filter_records_using_equal_to_attribute_to_get_only_records_whose_attributes_equal_to_something(
        self,
    ):
        test_obj_1 = models.TestItem(test_str="test_string", test_int=5)
        test_obj_2 = models.TestItem(test_str="test_string", test_int=8)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)
        objs_out = _db_access.get(
            tenants=self.tenant, base=models.TestItem, criteria={"test_int": lambda x: x == 5}
        )
        self.assertEqual(objs_out[0].test_int, test_obj_1.test_int)

    def test_filter_records_using_attribute_criteria(self):
        test_obj_1 = models.TestItem(test_str="test_string", test_int=5)
        test_obj_2 = models.TestItem(test_str="test_string", test_int=8)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)
        objs_out = _db_access.get(
            tenants=self.tenant, base=models.TestItem, criteria={"test_int": lambda x: x < 6}
        )
        self.assertEqual(objs_out[0].test_int, test_obj_1.test_int)
        objs_out = _db_access.get(
            tenants=self.tenant, base=models.TestItem, criteria={"test_int": lambda x: x > 6}
        )
        self.assertEqual(objs_out[0].test_int, test_obj_2.test_int)

    def test_sending_no_object_to_database_has_no_effect(self):
        _db_access.add(self.tenant)
        objs_out = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertListEqual(objs_out, [])


class Test_Updating_Records(api_test.TestCase):

    def setUp(self, *args, test_db_path: str = "", **kwargs) -> None:
        super().setUp(test_db_path)
        _set_up_test_data()
        self.tenant = TenantFromTokenMock(TEST_TENANT_NAME)

    def test_updating_an_existing_record(self):
        test_obj = models.TestItem(test_str="test_string", test_int=5)
        _db_access.add(self.tenant, test_obj)
        updated_obj = models.TestItem(id=1, test_str="updated_test_string", test_int=6)
        _db_access.update(self.tenant, updated_obj)
        retrieved_obj = _db_access.get(
            tenants=self.tenant, base=models.TestItem, criteria={"id": lambda x: x == 1}
        )[0]

        self.assertEqual(updated_obj.test_str, retrieved_obj.test_str)
        self.assertEqual(updated_obj.test_int, retrieved_obj.test_int)

    def test_updating_non_existing_record_yields_404_code(self):
        updated_obj = models.TestItem(id=2, test_str="updated_test_string", test_int=6)
        response = _db_access.update(self.tenant, updated_obj)
        self.assertEqual(response.status_code, 404)

    def test_updating_multiple_records_succesfully(self):
        test_obj_1 = models.TestItem(test_str="test_string", test_int=5)
        test_obj_2 = models.TestItem(test_str="test_string", test_int=8)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)
        updated_obj_1 = models.TestItem(id=1, test_str="updated_test_string", test_int=6)
        updated_obj_2 = models.TestItem(id=2, test_str="updated_test_string", test_int=9)
        _db_access.update(self.tenant, updated_obj_1, updated_obj_2)
        retrieved_objs = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertEqual(len(retrieved_objs), 2)
        self.assertEqual(retrieved_objs[0].test_int, updated_obj_1.test_int)
        self.assertEqual(retrieved_objs[1].test_int, updated_obj_2.test_int)

    def test_updating_multiple_records_with_one_failure_prevents_all_records_from_updating(self):
        obj_1 = models.TestItem(test_str="x", test_int=5)
        obj_2 = models.TestItem(test_str="y", test_int=8)
        _db_access.add(self.tenant, obj_1, obj_2)
        updated_obj_1 = models.TestItem(id=1, test_str="xxx", test_int=6)
        updated_obj_2 = models.TestItem(id=1651651213, test_str="yyy", test_int=9)
        response = _db_access.update(self.tenant, updated_obj_1, updated_obj_2)
        self.assertEqual(response.status_code, 404)
        retrieved_objs = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertEqual(len(retrieved_objs), 2)
        self.assertEqual(retrieved_objs[0].test_int, obj_1.test_int)
        self.assertEqual(retrieved_objs[1].test_int, obj_2.test_int)


class Test_Retrieving_Multiple_Records_By_Ids(api_test.TestCase):

    def setUp(self, *args, test_db_path: str = "", **kwargs) -> None:
        super().setUp(test_db_path)
        _set_up_test_data()
        self.tenant = TenantFromTokenMock(TEST_TENANT_NAME)

    def test_getting_items_by_id(self):
        test_obj_1 = models.TestItem(id=7, test_str="test_string", test_int=5)
        test_obj_2 = models.TestItem(id=8, test_str="test_string", test_int=18)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get_by_id(models.TestItem, 1)
        self.assertEqual(len(retrieved_objs), 1)
        self.assertEqual(retrieved_objs[0].test_int, test_obj_1.test_int)

        retrieved_objs = _db_access.get_by_id(models.TestItem, 1, 2)
        self.assertEqual(len(retrieved_objs), 2)
        self.assertEqual(retrieved_objs[0].test_int, 5)

    def test_using_only_nonexistent_ids_returns_empty_list(self):
        self.assertListEqual(_db_access.get_by_id(models.TestItem, 4, 5), [])


class Test_Deleting_Database_Record(api_test.TestCase):

    def setUp(self, *args, test_db_path: str = "", **kwargs) -> None:
        super().setUp(test_db_path)
        _set_up_test_data()
        self.tenant = TenantFromTokenMock(TEST_TENANT_NAME)

    def test_deleting_an_existing_record(self):
        test_obj = models.TestItem(id=7, test_str="test_string", test_int=5)
        _db_access.add(self.tenant, test_obj)
        _db_access.delete(self.tenant, base=models.TestItem, id_=7)
        retrieved_obj = _db_access.get(
            tenants=self.tenant, base=models.TestItem, criteria={"id": lambda x: x == 7}
        )
        self.assertListEqual(retrieved_obj, [])

    def test_deleting_non_existing_record_yields_404_code(self):
        nonexistent_obj_id = 112
        response = _db_access.delete(self.tenant, base=models.TestItem, id_=nonexistent_obj_id)
        self.assertEqual(response.status_code, 404)


class Test_Deleting_N_Database_Records(api_test.TestCase):

    def setUp(self, *args, test_db_path: str = "", **kwargs) -> None:
        super().setUp(test_db_path)
        _set_up_test_data()
        self.tenant = TenantFromTokenMock(TEST_TENANT_NAME)

    def test_deleting_n_records_with_least_ids(self):
        test_obj_1 = models.TestItem(test_str="aaa", test_int=5)
        test_obj_2 = models.TestItem(test_str="bbb", test_int=5)
        test_obj_3 = models.TestItem(test_str="ccc", test_int=5)
        _db_access.add(self.tenant, test_obj_3, test_obj_1, test_obj_2)

        _db_access.delete_n(base=models.TestItem, n=2, column_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(tenants=self.tenant, base=models.TestItem)
        test_obj_2.id = 3
        self.assertEqual(len(retrieved_objs), 1)
        self.assertEqual(retrieved_objs[0].test_str, test_obj_2.test_str)

    def test_deleting_n_records_with_highest_attribute_other_than_id(self):
        test_obj_1 = models.TestItem(test_str="aaa", test_int=9)
        test_obj_2 = models.TestItem(test_str="bbb", test_int=4)
        test_obj_3 = models.TestItem(test_str="ccc", test_int=5)
        _db_access.add(self.tenant, test_obj_1, test_obj_2, test_obj_3)
        _db_access.delete_n(base=models.TestItem, n=2, column_name="test_int", start_from="maximum")
        retrieved_objs = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertEqual(len(retrieved_objs), 1)
        self.assertEqual(retrieved_objs[0].test_str, test_obj_2.test_str)

    def test_deleting_n_records_with_highest_ids(self):
        test_obj_1 = models.TestItem(id=7, test_str="abc", test_int=2)
        test_obj_2 = models.TestItem(id=8, test_str="def", test_int=3)
        test_obj_3 = models.TestItem(id=4, test_str="ghi", test_int=4)
        _db_access.add(self.tenant, test_obj_3, test_obj_1, test_obj_2)
        _db_access.delete_n(models.TestItem, n=2, column_name="id", start_from="maximum")
        retrieved_objs: list[models.TestItem] = _db_access.get(
            tenants=self.tenant, base=models.TestItem
        )
        self.assertEqual(len(retrieved_objs), 1)
        self.assertEqual(retrieved_objs[0].test_str, test_obj_3.test_str)

    def test_if_attribute_chosen_as_id_for_sorting_does_not_exist_yields_code_500(self):
        response = _db_access.delete_n(
            models.TestItem, n=2, column_name="nonexistent_id", start_from="maximum"
        )
        self.assertEqual(response.status_code, 500)

    def test_setting_n_equal_to_or_greater_than_number_of_existing_records_deletes_all_records(
        self,
    ):
        test_obj_1 = models.TestItem(id=7, test_str="test_string", test_int=5)
        test_obj_2 = models.TestItem(id=8, test_str="test_string", test_int=5)
        _db_access.add(self.tenant, test_obj_1, test_obj_2)

        _db_access.delete_n(models.TestItem, n=3, column_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertListEqual(retrieved_objs, [])

    def test_removing_n_records_from_empty_table_has_no_effect(self):
        _db_access.delete_n(models.TestItem, n=2, column_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(tenants=self.tenant, base=models.TestItem)
        self.assertListEqual(retrieved_objs, [])

    def test_removing_n_filtered_records(self):
        test_obj_1 = models.TestItem(test_str="a", test_int=-1)
        test_obj_2 = models.TestItem(test_str="b", test_int=1)
        test_obj_3 = models.TestItem(test_str="c", test_int=-1)
        test_obj_4 = models.TestItem(test_str="e", test_int=1)
        test_obj_5 = models.TestItem(test_str="f", test_int=-1)
        test_obj_6 = models.TestItem(test_str="g", test_int=1)
        _db_access.add(
            self.tenant,
            test_obj_1,
            test_obj_2,
            test_obj_3,
            test_obj_4,
            test_obj_5,
            test_obj_6,
        )

        _db_access.delete_n(
            models.TestItem,
            n=2,
            column_name="id",
            start_from="minimum",
            criteria={"test_int": lambda x: x == -1},
        )

        remaining_objs_with_negative_test_int = _db_access.get(
            tenants=self.tenant, base=models.TestItem, criteria={"test_int": lambda x: x < 0}
        )
        test_obj_5.id = 5
        self.assertEqual(len(remaining_objs_with_negative_test_int), 1)
        self.assertEqual(remaining_objs_with_negative_test_int[0].test_str, test_obj_5.test_str)
        remaining_objs_with_positive_test_int = _db_access.get(
            tenants=self.tenant, base=models.TestItem, criteria={"test_int": lambda x: x > 0}
        )
        test_obj_2.id = 2
        test_obj_4.id = 4
        test_obj_6.id = 6
        self.assertEqual(len(remaining_objs_with_positive_test_int), 3)
        self.assertEqual(remaining_objs_with_positive_test_int[0].test_str, test_obj_2.test_str)
        self.assertEqual(remaining_objs_with_positive_test_int[1].test_str, test_obj_4.test_str)
        self.assertEqual(remaining_objs_with_positive_test_int[2].test_str, test_obj_6.test_str)


if __name__ == "__main__":
    unittest.main(verbosity=2)  # pragma: no cover
