import unittest
import sys

sys.path.append(".")

import fleet_management_api.database.db_access as _db_access
import tests.database.models as models
import tests.utils.api_test as api_test


class Test_Creating_Records(api_test.TestCase):

    def test_adding_single_record_to_database_succesfully(self):
        test_obj = models.TestBase(test_str="test_string", test_int=5)
        _db_access.add(test_obj)
        retrieved_obj = _db_access.get(models.TestBase)[0]
        self.assertEqual(retrieved_obj.test_str, test_obj.test_str)
        self.assertEqual(retrieved_obj.test_int, test_obj.test_int)

    def test_adding_multiple_records_to_database_succesfully(self):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=8)
        _db_access.add(test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertEqual(retrieved_objs[0].test_int, test_obj_1.test_int)
        self.assertEqual(retrieved_objs[1].test_int, test_obj_2.test_int)

    def test_single_failure_prevents_all_records_from_uploading_to_database(self):
        # failure is produced by the third record, having already taken ID
        test_obj_1 = models.TestBase(test_str="test_string", test_int=5, id=0)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=8, id=1)
        test_obj_3 = models.TestBase(test_str="test_string", test_int=9, id=1)
        response = _db_access.add(test_obj_1, test_obj_2, test_obj_3, auto_id=False)
        self.assertEqual(response.status_code, 400)
        records = _db_access.get(models.TestBase)
        self.assertListEqual(records, [])


class Test_Sending_And_Retrieving_From_Database(api_test.TestCase):

    def test_table_is_initially_empty(self):
        objs_out = _db_access.get(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_data_retrieved_are_equal_to_data_sent(self):
        data_in = models.TestBase(test_str="test_string", test_int=5)
        _db_access.add(data_in)
        data_out = _db_access.get(models.TestBase)[0]
        self.assertEqual(data_out.id, 1)
        self.assertEqual(data_out.test_str, data_in.test_str)
        self.assertEqual(data_out.test_int, data_in.test_int)

    def test_filter_records_using_equal_to_attribute_to_get_only_records_whose_attributes_equal_to_something(
        self,
    ):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=8)
        _db_access.add(test_obj_1, test_obj_2)
        objs_out = _db_access.get(models.TestBase, criteria={"test_int": lambda x: x == 5})
        self.assertEqual(objs_out[0].test_int, test_obj_1.test_int)

    def test_filter_records_using_attribute_criteria(self):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=8)
        _db_access.add(test_obj_1, test_obj_2)
        objs_out = _db_access.get(models.TestBase, criteria={"test_int": lambda x: x < 6})
        self.assertEqual(objs_out[0].test_int, test_obj_1.test_int)
        objs_out = _db_access.get(models.TestBase, criteria={"test_int": lambda x: x > 6})
        self.assertEqual(objs_out[0].test_int, test_obj_2.test_int)

    def test_sending_no_object_to_database_has_no_effect(self):
        _db_access.add(
            models.TestBase,
        )
        objs_out = _db_access.get(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_sending_obj_whose_base_does_not_match_specified_base_type_raises_exception(
        self,
    ):
        base_type = models.TestBase
        db_obj = models.TestBase2(id=8, test_str_2="test_string", test_int_2=5)
        with self.assertRaises(TypeError):
            _db_access.add(base_type, db_obj)


class Test_Updating_Records(api_test.TestCase):

    def test_updating_an_existing_record(self):
        test_obj = models.TestBase(test_str="test_string", test_int=5)
        _db_access.add(test_obj)
        updated_obj = models.TestBase(id=1, test_str="updated_test_string", test_int=6)
        _db_access.update(updated_obj)
        retrieved_obj = _db_access.get(models.TestBase, criteria={"id": lambda x: x == 1})[0]
        self.assertEqual(updated_obj, retrieved_obj)

    def test_updating_non_existing_record_yields_404_code(self):
        updated_obj = models.TestBase(id=2, test_str="updated_test_string", test_int=6)
        response = _db_access.update(updated_obj)
        self.assertEqual(response.status_code, 404)

    def test_updating_multiple_records_succesfully(self):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=8)
        _db_access.add(test_obj_1, test_obj_2)
        updated_obj_1 = models.TestBase(id=1, test_str="updated_test_string", test_int=6)
        updated_obj_2 = models.TestBase(id=2, test_str="updated_test_string", test_int=9)
        _db_access.update(updated_obj_1, updated_obj_2)
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertEqual(retrieved_objs, [updated_obj_1, updated_obj_2])

    def test_updating_multiple_records_with_one_failure_prevents_all_records_from_updating(self):
        obj_1 = models.TestBase(test_str="x", test_int=5)
        obj_2 = models.TestBase(test_str="y", test_int=8)
        _db_access.add(obj_1, obj_2)
        updated_obj_1 = models.TestBase(id=1, test_str="xxx", test_int=6)
        updated_obj_2 = models.TestBase(id=1651651213, test_str="yyy", test_int=9)
        response = _db_access.update(updated_obj_1, updated_obj_2)
        self.assertEqual(response.status_code, 404)
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertEqual(retrieved_objs, [obj_1, obj_2])


class Test_Retrieving_Multiple_Records_By_Ids(api_test.TestCase):

    def test_getting_items_by_id(self):
        test_obj_1 = models.TestBase(id=7, test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str="test_string", test_int=18)
        _db_access.add(test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get_by_id(models.TestBase, 1)
        self.assertEqual(len(retrieved_objs), 1)
        self.assertEqual(retrieved_objs[0].test_int, test_obj_1.test_int)

        retrieved_objs = _db_access.get_by_id(models.TestBase, 1, 2)
        self.assertEqual(len(retrieved_objs), 2)
        self.assertEqual(retrieved_objs[0].test_int, 5)

    def test_using_only_nonexistent_ids_returns_empty_list(self):
        self.assertListEqual(_db_access.get_by_id(models.TestBase, 4, 5), [])


class Test_Deleting_Database_Record(api_test.TestCase):

    def test_deleting_an_existing_record(self):
        test_obj = models.TestBase(id=7, test_str="test_string", test_int=5)
        _db_access.add(test_obj)
        _db_access.delete(base=models.TestBase, id_=7)
        retrieved_obj = _db_access.get(models.TestBase, criteria={"id": lambda x: x == 7})
        self.assertListEqual(retrieved_obj, [])

    def test_deleting_non_existing_record_yields_404_code(self):
        nonexistent_obj_id = 112
        response = _db_access.delete(base=models.TestBase, id_=nonexistent_obj_id)
        self.assertEqual(response.status_code, 404)


class Test_Deleting_N_Database_Records(api_test.TestCase):

    def test_deleting_n_records_with_least_ids(self):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=5)
        test_obj_3 = models.TestBase(test_str="test_string", test_int=5)
        _db_access.add(test_obj_3, test_obj_1, test_obj_2)

        _db_access.delete_n(models.TestBase, n=2, column_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(models.TestBase)
        test_obj_2.id = 3
        self.assertListEqual(retrieved_objs, [test_obj_2])

    def test_deleting_n_records_with_highest_ids(self):
        test_obj_1 = models.TestBase(id=7, test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str="test_string", test_int=5)
        test_obj_3 = models.TestBase(id=4, test_str="test_string", test_int=5)
        _db_access.add(test_obj_3, test_obj_1, test_obj_2)
        _db_access.delete_n(models.TestBase, n=2, column_name="id", start_from="maximum")
        retrieved_objs = _db_access.get(models.TestBase)
        test_obj_3.id = 1
        self.assertListEqual(retrieved_objs, [test_obj_3])

    def test_if_attribute_chosen_as_id_for_sorting_does_not_exist_yields_code_500(self):
        response = _db_access.delete_n(
            models.TestBase, n=2, column_name="nonexistent_id", start_from="maximum"
        )
        self.assertEqual(response.status_code, 500)

    def test_setting_n_equal_to_or_greater_than_number_of_existing_records_deletes_all_records(
        self,
    ):
        test_obj_1 = models.TestBase(id=7, test_str="test_string", test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str="test_string", test_int=5)
        _db_access.add(test_obj_1, test_obj_2)

        _db_access.delete_n(models.TestBase, n=3, column_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertListEqual(retrieved_objs, [])

    def test_removing_n_records_from_empty_table_has_no_effect(self):
        _db_access.delete_n(models.TestBase, n=2, column_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertListEqual(retrieved_objs, [])

    def test_removing_n_filtered_records(self):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=-1)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=1)
        test_obj_3 = models.TestBase(test_str="test_string", test_int=-1)
        test_obj_4 = models.TestBase(test_str="test_string", test_int=1)
        test_obj_5 = models.TestBase(test_str="test_string", test_int=-1)
        test_obj_6 = models.TestBase(test_str="test_string", test_int=1)
        _db_access.add(
            test_obj_1,
            test_obj_2,
            test_obj_3,
            test_obj_4,
            test_obj_5,
            test_obj_6,
        )

        _db_access.delete_n(
            models.TestBase,
            n=2,
            column_name="id",
            start_from="minimum",
            criteria={"test_int": lambda x: x == -1},
        )

        remaining_objs_with_negative_test_int = _db_access.get(
            models.TestBase, criteria={"test_int": lambda x: x < 0}
        )
        test_obj_5.id = 5
        self.assertListEqual(remaining_objs_with_negative_test_int, [test_obj_5])
        remaining_objs_with_positive_test_int = _db_access.get(
            models.TestBase, criteria={"test_int": lambda x: x > 0}
        )
        test_obj_2.id = 2
        test_obj_4.id = 4
        test_obj_6.id = 6
        self.assertListEqual(
            remaining_objs_with_positive_test_int, [test_obj_2, test_obj_4, test_obj_6]
        )


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
