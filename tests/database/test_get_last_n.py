import unittest
import sys
import os

sys.path.append(".")

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access
import tests.database.models as models


class Test_Retrieving_Last_N_Records(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test(db_file_path = "tests/database/test_get_last_n.db")
        models.initialize_test_tables(_connection.current_connection_source())

    def test_retrieving_single_item_with_highest_attribute_value(self):
        test_obj_1 = models.TestBase(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestBase(id=8, test_str="test_string", test_int=100)
        _db_access.add(test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get(models.TestBase, first_n=1, sort_result_by={"test_int": "desc"})
        self.assertEqual(len(retrieved_objs), 1)
        self.assertEqual(retrieved_objs[0].test_int, 150)

    def test_retrieving_both_items_sorted_by_attribute_value_in_descending_order(self):
        test_obj_1 = models.TestBase(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestBase(id=8, test_str="test_string", test_int=100)
        _db_access.add(test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get(models.TestBase, first_n=2, sort_result_by={"test_int": "desc"})
        self.assertEqual(retrieved_objs[0].test_int, 150)
        self.assertEqual(retrieved_objs[1].test_int, 100)

    def test_retrieving_the_two_items_with_highest_attribute_value(self):
        test_obj_1 = models.TestBase(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestBase(id=8, test_str="test_string", test_int=100)
        test_obj_2 = models.TestBase(id=9, test_str="test_string", test_int=120)
        _db_access.add(test_obj_1, test_obj_2)
        retrieved_objs = _db_access.get(models.TestBase, first_n=2, sort_result_by={"test_int": "desc"})
        self.assertEqual(len(retrieved_objs), 2)
        self.assertEqual(retrieved_objs[0].test_int, 150)
        self.assertEqual(retrieved_objs[1].test_int, 120)

    def test_retrieving_the_two_items_with_lowest_attribute_value(self):
        test_obj_1 = models.TestBase(id=7, test_str="test_string", test_int=150)
        test_obj_2 = models.TestBase(id=8, test_str="test_string", test_int=100)
        test_obj_3 = models.TestBase(id=9, test_str="test_string", test_int=120)
        _db_access.add(test_obj_1, test_obj_2, test_obj_3)
        retrieved_objs = _db_access.get(models.TestBase, first_n=3, sort_result_by={"test_int": "asc"})
        self.assertEqual(retrieved_objs[0].test_int, 100)
        self.assertEqual(retrieved_objs[1].test_int, 120)

    def test_returning_items_with_highest_value_of_a_second_attribute_if_first_attribute_values_are_equal(self):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=100)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=100)
        test_obj_3 = models.TestBase(test_str="test_string", test_int=120)
        _db_access.add(test_obj_1, test_obj_2, test_obj_3)
        retrieved_objs = _db_access.get(
            models.TestBase,
            first_n=2,
            sort_result_by={"test_int": "desc", "id": "desc"}
        )
        self.assertEqual(retrieved_objs[0].test_int, 120)
        self.assertEqual(retrieved_objs[0].id, 3)
        self.assertEqual(retrieved_objs[1].test_int, 100)
        self.assertEqual(retrieved_objs[1].id, 2)

    def test_returning_items_with_lowest_value_of_a_second_attribute_if_first_attribute_values_are_equal(self):
        test_obj_1 = models.TestBase(test_str="test_string", test_int=100)
        test_obj_2 = models.TestBase(test_str="test_string", test_int=100)
        test_obj_3 = models.TestBase(test_str="test_string", test_int=120)
        _db_access.add(test_obj_1, test_obj_2, test_obj_3)
        retrieved_objs = _db_access.get(
            models.TestBase,
            first_n=2,
            sort_result_by={"test_int": "desc", "id": "asc"}
        )
        self.assertEqual(retrieved_objs[0].test_int, 120)
        self.assertEqual(retrieved_objs[0].id, 3)
        self.assertEqual(retrieved_objs[1].test_int, 100)
        self.assertEqual(retrieved_objs[1].id, 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("tests/database/test_get_last_n.db"):
            os.remove("tests/database/test_get_last_n.db")


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
