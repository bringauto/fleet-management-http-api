import unittest
import sys
sys.path.append('.')

import fleet_management_api.database.connection as connection
import fleet_management_api.database.db_access as _db_access
import tests.database.models as models


class Test_Sending_And_Retrieving_From_Database(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_table_is_initially_empty(self):
        objs_out = _db_access.get(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_data_retrieved_are_equal_to_data_sent(self):
        data_in = models.TestBase(id=8, test_str='test_string', test_int=5)
        _db_access.add(models.TestBase, data_in)
        data_out = _db_access.get(models.TestBase)[0]
        self.assertEqual(data_out, data_in)

    def test_filter_records_using_equal_to_attribute_to_get_only_records_whose_attributes_equal_to_something(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=8)
        _db_access.add(models.TestBase, test_obj_1, test_obj_2)
        objs_out = _db_access.get(models.TestBase, criteria={'test_int': lambda x: x==5})
        self.assertListEqual(objs_out, [test_obj_1])

    def test_filter_records_using_attribute_criteria(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=8)
        _db_access.add(models.TestBase, test_obj_1, test_obj_2)
        objs_out = _db_access.get(models.TestBase, criteria = {'test_int': lambda x: x < 6})
        self.assertListEqual(objs_out, [test_obj_1])
        objs_out = _db_access.get(models.TestBase, criteria = {'test_int': lambda x: x > 6})
        self.assertListEqual(objs_out, [test_obj_2])

    def test_sending_no_object_to_database_has_no_effect(self):
        _db_access.add(models.TestBase, )
        objs_out = _db_access.get(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_sending_obj_whose_base_does_not_match_specified_base_type_raises_exception(self):
        base_type = models.TestBase
        db_obj = models.TestBase2(id=8, test_str_2='test_string', test_int_2=5)
        with self.assertRaises(TypeError):
            _db_access.add(base_type, db_obj)


class Test_Updating_Records(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_updating_an_existing_record(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        _db_access.add(models.TestBase, test_obj)
        updated_obj = models.TestBase(id=7, test_str='updated_test_string', test_int=6)
        _db_access.update(updated_obj=updated_obj)
        retrieved_obj = _db_access.get(models.TestBase, criteria={'id': lambda x: x==7})[0]
        self.assertEqual(updated_obj, retrieved_obj)

    def test_updating_non_existing_record_yields_404_code(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        _db_access.add(models.TestBase, test_obj)
        updated_obj = models.TestBase(id=8, test_str='updated_test_string', test_int=6)
        response = _db_access.update(updated_obj=updated_obj)
        self.assertEqual(response.status_code, 404)


class Test_Deleting_Database_Record(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_deleting_an_existing_record(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        _db_access.add(models.TestBase, test_obj)
        _db_access.delete(base_type=models.TestBase, id_name="id", id_value=7)
        retrieved_obj = _db_access.get(models.TestBase, criteria={'id': lambda x: x==7})
        self.assertListEqual(retrieved_obj, [])

    def test_deleting_non_existing_record_yields_404_code(self):
        nonexistent_obj_id = 112
        response = _db_access.delete(base_type=models.TestBase, id_name="id", id_value=nonexistent_obj_id)
        self.assertEqual(response.status_code, 404)


class Test_Deleting_N_Database_Records(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_deleting_n_records_with_least_ids(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=5)
        test_obj_3 = models.TestBase(id=4, test_str='test_string', test_int=5)
        _db_access.add(models.TestBase, test_obj_1, test_obj_2, test_obj_3)

        _db_access.delete_n(models.TestBase, n=2, id_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertListEqual(retrieved_objs, [test_obj_2])

    def test_deleting_n_records_with_highest_ids(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=5)
        test_obj_3 = models.TestBase(id=4, test_str='test_string', test_int=5)
        _db_access.add(models.TestBase, test_obj_1, test_obj_2, test_obj_3)

        _db_access.delete_n(models.TestBase, n=2, id_name="id", start_from="maximum")
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertListEqual(retrieved_objs, [test_obj_3])

    def test_if_attribute_chosen_as_id_for_sorting_does_not_exist_yields_code_500(self):
        response = _db_access.delete_n(models.TestBase, n=2, id_name="nonexistent_id", start_from="maximum")
        self.assertEqual(response.status_code, 500)

    def test_setting_n_equal_to_or_greater_than_number_of_existing_records_deletes_all_records(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=5)
        _db_access.add(models.TestBase, test_obj_1, test_obj_2)

        _db_access.delete_n(models.TestBase, n=3, id_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertListEqual(retrieved_objs, [])

    def test_removing_n_records_from_empty_table_has_no_effect(self):
        _db_access.delete_n(models.TestBase, n=2, id_name="id", start_from="minimum")
        retrieved_objs = _db_access.get(models.TestBase)
        self.assertListEqual(retrieved_objs, [])


if __name__=="__main__":
    unittest.main() # pragma: no cover
