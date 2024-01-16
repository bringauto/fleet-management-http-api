import unittest

import fleet_management_api.database.db_models as db_models
import fleet_management_api.database.connection as connection


class Test_Sending_Data_To_Database(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()

    def test_table_is_initially_empty(self):
        objs_out = connection.retrieve_from_database(db_models.TestBase)
        self.assertListEqual(objs_out, [])

    def test_data_retrieved_are_equal_to_data_sent(self):
        data_in = db_models.TestBase(id=8, test_str='test_string', test_int=5)
        connection.send_to_database(db_models.TestBase, data_in)
        data_out = connection.retrieve_from_database(db_models.TestBase)[0]
        self.assertEqual(data_out, data_in)

    def test_filter_attribute_of_given_value(self):
        test_obj_1 = db_models.TestBase(id=7, test_str='test_string', test_int=5)
        test_obj_2 = db_models.TestBase(id=8, test_str='test_string', test_int=8)
        connection.send_to_database(db_models.TestBase, test_obj_1, test_obj_2)
        objs_out = connection.retrieve_from_database(db_models.TestBase, equal_to = {'test_int': 5})
        self.assertListEqual(objs_out, [test_obj_1])

    def test_sending_no_object_to_database_has_no_effect(self):
        connection.send_to_database(db_models.TestBase, )
        objs_out = connection.retrieve_from_database(db_models.TestBase)
        self.assertListEqual(objs_out, [])


if __name__=="__main__":
    unittest.main() # pragma: no cover