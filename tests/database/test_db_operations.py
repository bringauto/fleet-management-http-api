import unittest
import sys
sys.path.append('.')

import fleet_management_api.database.connection as connection
import fleet_management_api.database.db_access as db_access
import tests.database.models as models


class Test_Sending_And_Retrieving_From_Database(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_table_is_initially_empty(self):
        objs_out = db_access.get_records(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_data_retrieved_are_equal_to_data_sent(self):
        data_in = models.TestBase(id=8, test_str='test_string', test_int=5)
        db_access.add_record(models.TestBase, data_in)
        data_out = db_access.get_records(models.TestBase)[0]
        self.assertEqual(data_out, data_in)

    def test_filter_attribute_of_given_value(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=8)
        db_access.add_record(models.TestBase, test_obj_1, test_obj_2)
        objs_out = db_access.get_records(models.TestBase, equal_to = {'test_int': 5})
        self.assertListEqual(objs_out, [test_obj_1])

    def test_sending_no_object_to_database_has_no_effect(self):
        db_access.add_record(models.TestBase, )
        objs_out = db_access.get_records(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_sending_obj_whose_base_does_not_match_specified_base_type_raises_exception(self):
        base_type = models.TestBase
        db_obj = models.TestBase2(id=8, test_str_2='test_string', test_int_2=5)
        with self.assertRaises(TypeError):
            db_access.add_record(base_type, db_obj)


class Test_Updating_Records(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_updating_an_existing_record(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        db_access.add_record(models.TestBase, test_obj)
        updated_obj = models.TestBase(id=7, test_str='updated_test_string', test_int=6)
        db_access.update_record(updated_obj=updated_obj)
        retrieved_obj = db_access.get_records(models.TestBase, equal_to={'id':7})[0]
        self.assertEqual(updated_obj, retrieved_obj)

    def test_updating_non_existing_record_yields_404_code(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        db_access.add_record(models.TestBase, test_obj)
        updated_obj = models.TestBase(id=8, test_str='updated_test_string', test_int=6)
        response = db_access.update_record(updated_obj=updated_obj)
        self.assertEqual(response.status_code, 404)


class Test_Deleting_Database_Record(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_deleting_an_existing_record(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        db_access.add_record(models.TestBase, test_obj)
        db_access.delete_record(base_type=models.TestBase, id_name="id", id_value=7)
        retrieved_obj = db_access.get_records(models.TestBase, equal_to={'id':7})
        self.assertListEqual(retrieved_obj, [])

    def test_deleting_non_existing_record_yields_404_code(self):
        nonexistent_obj_id = 112
        response = db_access.delete_record(base_type=models.TestBase, id_name="id", id_value=nonexistent_obj_id)
        self.assertEqual(response.status_code, 404)


class Test_Deleting_N_Database_Records(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_deleting_n_records_with_least_ids(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=5)
        test_obj_3 = models.TestBase(id=4, test_str='test_string', test_int=5)
        db_access.add_record(models.TestBase, test_obj_1, test_obj_2, test_obj_3)

        db_access.delete_n_records(models.TestBase, n=2, id_name="id", start_from="minimum")
        retrieved_objs = db_access.get_records(models.TestBase)
        self.assertListEqual(retrieved_objs, [test_obj_2])

    def test_deleting_n_records_with_highest_ids(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=5)
        test_obj_3 = models.TestBase(id=4, test_str='test_string', test_int=5)
        db_access.add_record(models.TestBase, test_obj_1, test_obj_2, test_obj_3)

        db_access.delete_n_records(models.TestBase, n=2, id_name="id", start_from="maximum")
        retrieved_objs = db_access.get_records(models.TestBase)
        self.assertListEqual(retrieved_objs, [test_obj_3])


if __name__=="__main__":
    unittest.main() # pragma: no cover
