import unittest
import sys
sys.path.append('.')

import fleet_management_api.database.connection as connection
import fleet_management_api.database.db_access as db_access
import tests.database.models as models


class Test_Sending_Data_To_Database(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_table_is_initially_empty(self):
        objs_out = db_access.retrieve_from_database(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_data_retrieved_are_equal_to_data_sent(self):
        data_in = models.TestBase(id=8, test_str='test_string', test_int=5)
        db_access.send_to_database(models.TestBase, data_in)
        data_out = db_access.retrieve_from_database(models.TestBase)[0]
        self.assertEqual(data_out, data_in)

    def test_filter_attribute_of_given_value(self):
        test_obj_1 = models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = models.TestBase(id=8, test_str='test_string', test_int=8)
        db_access.send_to_database(models.TestBase, test_obj_1, test_obj_2)
        objs_out = db_access.retrieve_from_database(models.TestBase, equal_to = {'test_int': 5})
        self.assertListEqual(objs_out, [test_obj_1])

    def test_sending_no_object_to_database_has_no_effect(self):
        db_access.send_to_database(models.TestBase, )
        objs_out = db_access.retrieve_from_database(models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_sending_obj_whose_base_does_not_match_specified_base_type_raises_exception(self):
        base_type = models.TestBase
        db_obj = models.TestBase2(id=8, test_str_2='test_string', test_int_2=5)
        with self.assertRaises(TypeError):
            db_access.send_to_database(base_type, db_obj)


class Test_Updating_Existing_Records(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        models.initialize_test_tables(connection.current_connection_source())

    def test_updating_an_existing_record(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        db_access.send_to_database(models.TestBase, test_obj)
        updated_obj = models.TestBase(id=7, test_str='updated_test_string', test_int=6)
        db_access.update_record(id_name="id", id_value=7, updated_obj=updated_obj)
        retrieved_obj = db_access.retrieve_from_database(models.TestBase, equal_to={'id':7})[0]
        self.assertEqual(updated_obj, retrieved_obj)

    def test_updating_non_existing_record_yields_404_code(self):
        test_obj = models.TestBase(id=7, test_str='test_string', test_int=5)
        db_access.send_to_database(models.TestBase, test_obj)
        updated_obj = models.TestBase(id=8, test_str='updated_test_string', test_int=6)
        response = db_access.update_record(id_name="id", id_value=8, updated_obj=updated_obj)
        self.assertEqual(response.status_code, 404)


if __name__=="__main__":
    unittest.main() # pragma: no cover
