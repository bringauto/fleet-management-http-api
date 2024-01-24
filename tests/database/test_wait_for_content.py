import unittest
import sys
sys.path.append('.')
import os
from concurrent.futures import ThreadPoolExecutor
import time

import fleet_management_api.database.connection as connection
import fleet_management_api.database.db_access as db_access
import tests.database.models as models
import fleet_management_api.database.wait as wait


_TEST_DB_FILE_PATH = "test_db_file.db"


class Test_Wait_Objects(unittest.TestCase):

    def test_setting_default_timeout(self) -> None:
        wait_manager = wait.WaitObjManager()
        wait_manager.set_timeout(1234)
        self.assertEqual(wait_manager.timeout_ms, 1234)
        wait_manager.set_timeout(4567)
        self.assertEqual(wait_manager.timeout_ms, 4567)

    def test_setting_negative_timeout_raises_value_error(self) -> None:
        wait_manager = wait.WaitObjManager()
        with self.assertRaises(ValueError):
            wait_manager.set_timeout(-4567)

    def test_initializing_wait_obj_with_negative_timeout_set_it_to_zero(self) -> None:
        wait_obj = wait.WaitObj("key", timeout_ms=-1234)
        self.assertEqual(wait_obj.timeout_ms, 0)

    def test_content_filtered_by_wait_obj_with_validation_set_to_none_returns_the_unfiltered_content(self):
        wait_obj = wait.WaitObj("key", timeout_ms=5000, validation=None)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), content)

    def test_content_filtered_by_wait_obj_with_validation_set_to_true_returns_the_unfiltered_content(self):
        wait_obj = wait.WaitObj("key", timeout_ms=5000, validation=lambda x: True)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), content)

    def test_content_filtered_by_wait_obj_with_validation_set_to_false_returns_empty_list(self):
        wait_obj = wait.WaitObj("key", timeout_ms=5000, validation=lambda x: False)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), [])

    def test_content_filtered_by_wait_obj_with_validation_set_to_filtering_function_returns_filtered_content(self):
        wait_obj = wait.WaitObj("key", timeout_ms=5000, validation=lambda x: x>2)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), [3,4,5])

    def test_removing_wait_object_for_which_no_key_exists_in_the_wait_obj_manager_dict_raises_key_error(self):
        wait_obj = wait.WaitObj("key", timeout_ms=5000, validation=None)
        wait_manager = wait.WaitObjManager()
        with self.assertRaises(wait.WaitObjManager.UnknownWaitingObj):
            wait_manager._remove_wait_obj(wait_obj)


class Test_Waiting_For_Content(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source(_TEST_DB_FILE_PATH)
        models.initialize_test_tables(connection.current_connection_source())

    def test_enabling_wait_mechanism_makes_the_db_request_wait_for_available_content_and_to_return_nonempty_list(self):
        test_obj = models.TestBase(id=5, test_str="test", test_int=123)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(db_access.get_records, models.TestBase, wait=True)
            executor.submit(db_access.add_record, models.TestBase, test_obj)
            retrieved_objs = future.result()
            self.assertEqual(retrieved_objs, [test_obj])

    def test_not_enabling_wait_mechanism_when_no_content_is_available_makes_the_db_request_immediatelly_return_empty_list(self):
        test_obj = models.TestBase(id=5, test_str="test", test_int=123)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(db_access.get_records, models.TestBase, wait=False)
            time.sleep(0.05)
            executor.submit(db_access.add_record, models.TestBase, test_obj)
            retrieved_objs = future.result()
            self.assertListEqual(retrieved_objs, [])

    def test_exceeding_timeout_makes_the_db_to_stop_waiting_and_return_empty_list(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(db_access.get_records, models.TestBase, wait=True, timeout_ms=100)
            retrieved_objs = future.result()
            self.assertListEqual(retrieved_objs, [])

    def test_response_is_sent_to_multiple_waiters(self):
        test_obj = models.TestBase(id=5, test_str="test", test_int=123)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future1 = executor.submit(db_access.get_records, models.TestBase, wait=True, timeout_ms=1000)
            future2 = executor.submit(db_access.get_records, models.TestBase, wait=True, timeout_ms=1000)
            time.sleep(0.05)
            executor.submit(db_access.add_record, models.TestBase, test_obj)
            retrieved_objs1 = future1.result()
            retrieved_objs2 = future2.result()
            self.assertEqual(retrieved_objs1, [test_obj])
            self.assertEqual(retrieved_objs2, [test_obj])

    def tearDown(self) -> None:
        if os.path.isfile(_TEST_DB_FILE_PATH):
            os.remove(_TEST_DB_FILE_PATH)


class Test_Waiting_For_Specific_Content(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source(_TEST_DB_FILE_PATH)
        models.initialize_test_tables(connection.current_connection_source())

    def test_waiting_mechanism_ignores_content_with_properties_not_matching_requested_values(self):
        test_obj = models.TestBase(id=5, test_str="test", test_int=123)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(
                db_access.get_records,
                models.TestBase,
                equal_to={"test_int": 456},
                wait=True,
                timeout_ms=500
            )
            time.sleep(0.01)
            executor.submit(db_access.add_record, models.TestBase, test_obj)
            time.sleep(0.01)
            retrieved_objs = future.result()
            self.assertListEqual(retrieved_objs, [])

    def tearDown(self) -> None:
        if os.path.isfile(_TEST_DB_FILE_PATH):
            os.remove(_TEST_DB_FILE_PATH)


class Test_Waiting_For_New_Content_To_Be_Sent(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source(_TEST_DB_FILE_PATH)
        models.initialize_test_tables(connection.current_connection_source())

    def test_waiting_for_new_record_to_be_sent_to_database(self):
        old_record = models.TestBase(id=111, test_str="test_1", test_int=123)
        new_record = models.TestBase(id=222, test_str="test_2", test_int=456)
        db_access.add_record(models.TestBase, old_record)
        with ThreadPoolExecutor(max_workers=3) as executor:
            future = executor.submit(
                db_access.wait_for_new_records,
                models.TestBase,
                timeout_ms=5000
            )
            time.sleep(0.5)
            executor.submit(db_access.add_record, models.TestBase, new_record)
            time.sleep(0.05)
            retrieved_objs = future.result()
            self.assertListEqual(retrieved_objs, [new_record])

    def tearDown(self) -> None:
        if os.path.isfile(_TEST_DB_FILE_PATH):
            os.remove(_TEST_DB_FILE_PATH)


if __name__=="__main__":
    unittest.main() # pragma: no covers