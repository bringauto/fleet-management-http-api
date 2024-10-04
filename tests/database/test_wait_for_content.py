import unittest
from concurrent.futures import ThreadPoolExecutor
import time

from sqlalchemy.pool.impl import QueuePool

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access
import tests.database.models as models
import fleet_management_api.database.wait as wait
import tests._utils.api_test as api_test


class Test_Wait_Objects(unittest.TestCase):
    def test_setting_default_timeout(self) -> None:
        wait_manager = wait.WaitObjManager()
        wait_manager.set_default_timeout(1234)
        self.assertEqual(wait_manager.timeout_ms, 1234)
        wait_manager.set_default_timeout(4567)
        self.assertEqual(wait_manager.timeout_ms, 4567)

    def test_setting_negative_timeout_raises_value_error(self) -> None:
        wait_manager = wait.WaitObjManager()
        with self.assertRaises(ValueError):
            wait_manager.set_default_timeout(-4567)

    def test_initializing_wait_obj_with_negative_timeout_set_it_to_zero(self) -> None:
        wait_obj = wait.WaitObject(timeout_ms=-1234)
        self.assertEqual(wait_obj._timeout_ms, 0)

    def test_content_filtered_with_validation_set_to_none_returns_unfiltered_content(self):
        wait_obj = wait.WaitObject(timeout_ms=5000, validation=None)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), content)

    def test_content_filtered_with_validation_set_to_true_returns_the_unfiltered_content(self):
        wait_obj = wait.WaitObject(timeout_ms=5000, validation=lambda x: True)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), content)

    def test_content_filtered_by_wait_obj_with_validation_set_to_false_returns_empty_list(self):
        wait_obj = wait.WaitObject(timeout_ms=5000, validation=lambda x: False)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), [])

    def test_content_filtered_with_filtering_function_returns_filtered_content(self):
        wait_obj = wait.WaitObject(timeout_ms=5000, validation=lambda x: x > 2)
        content = [1, 2, 3, 4, 5]
        self.assertListEqual(wait_obj.filter_content(content), [3, 4, 5])

    def test_removing_wait_object_for_which_no_key_exists_raises_key_error(self):
        wait_obj = wait.WaitObject(timeout_ms=5000, validation=None)
        wait_manager = wait.WaitObjManager()
        with self.assertRaises(wait.WaitObjManager.UnknownWaitingObj):
            wait_manager._remove_wait_obj("nonexistent key", wait_obj)


class Test_Waiting_For_Content(api_test.TestCase):

    def test_enabling_wait_mechanism_makes_the_db_request_wait_for_available_content_and_to_return_nonempty_list(
        self,
    ):
        test_obj = models.TestBase(test_str="test", test_int=123)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(_db_access.get, models.TestBase, wait=True)
            executor.submit(_db_access.add, test_obj)
            retrieved_objs = future.result()
            self.assertEqual(retrieved_objs[0].test_str, test_obj.test_str)

    def test_not_enabling_wait_mechanism_and_unavailable_content_immediatelly_returns_empty_list(
        self,
    ):
        test_obj = models.TestBase(test_str="test", test_int=123)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(_db_access.get, models.TestBase, wait=False)
            time.sleep(0.05)
            executor.submit(_db_access.add, test_obj)
            retrieved_objs = future.result()
            self.assertListEqual(retrieved_objs, [])

    def test_exceeding_timeout_makes_the_db_to_stop_waiting_and_return_empty_list(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(_db_access.get, models.TestBase, wait=True, timeout_ms=100)
            retrieved_objs = future.result()
            self.assertListEqual(retrieved_objs, [])

    def test_response_is_sent_to_multiple_waiters(self):
        test_obj = models.TestBase(test_str="test_x", test_int=123)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future1 = executor.submit(_db_access.get, models.TestBase, wait=True, timeout_ms=1000)
            future2 = executor.submit(_db_access.get, models.TestBase, wait=True, timeout_ms=1000)
            time.sleep(0.05)
            executor.submit(_db_access.add, test_obj)
            retrieved_objs1 = future1.result()
            retrieved_objs2 = future2.result()
            self.assertEqual(retrieved_objs1[0].test_str, test_obj.test_str)
            self.assertEqual(retrieved_objs2[0].test_str, test_obj.test_str)


class Test_Waiting_For_Specific_Content(api_test.TestCase):

    def test_waiting_mechanism_ignores_content_with_properties_not_matching_requested_values(self):
        test_obj = models.TestBase(id=5, test_str="test", test_int=123)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(
                _db_access.get,
                models.TestBase,
                criteria={"test_int": lambda x: x == 456},
                wait=True,
                timeout_ms=500,
            )
            time.sleep(0.01)
            executor.submit(_db_access.add, test_obj)
            time.sleep(0.01)
            retrieved_objs = future.result()
            self.assertListEqual(retrieved_objs, [])


class Test_Waiting_For_New_Content_To_Be_Sent(api_test.TestCase):

    def test_waiting_for_new_record_to_be_sent_to_database(self):
        old_record = models.TestBase(id=111, test_str="test_1", test_int=123)
        new_record = models.TestBase(id=222, test_str="test_2", test_int=456)
        _db_access.add(old_record)
        with ThreadPoolExecutor(max_workers=3) as executor:
            future = executor.submit(_db_access.wait_for_new, models.TestBase, timeout_ms=5000)
            time.sleep(0.5)
            executor.submit(_db_access.add, new_record)
            time.sleep(0.05)
            retrieved_objs = future.result()
            self.assertEqual(len(retrieved_objs), 1)
            self.assertEqual(retrieved_objs[0].test_str, new_record.test_str)


class Test_Waiting_Mechanism_Releases_Connection_To_Pool(api_test.TestCase):
    """There is a maximum number of active connections that can be opened at the same time.

    To reduce the number of connections, the waiting mechanism should release the connection
    if there are no data available. This test checks if the connection is released back to the
    connection pool.

    This releasing of a connection is possible, because the waiting request on the HTTP server
    waits for data coming from other request to the server and does not read them from the database.
    """

    def test_single_connection_is_reused_by_every_request_and_then_checked_in_into_pool(self):
        test_obj = models.TestBase(test_str="test", test_int=123)
        src = _connection.current_connection_source()
        assert isinstance(src.pool, QueuePool)
        def get_and_count_connections():
            _db_access.get(models.TestBase, wait=True)

        with ThreadPoolExecutor() as executor:
            executor.submit(get_and_count_connections)
            time.sleep(0.01)
            executor.submit(get_and_count_connections)
            time.sleep(0.01)
            executor.submit(get_and_count_connections)
            time.sleep(0.01)
            executor.submit(_db_access.add, test_obj)
            time.sleep(0.02)
            self.assertEqual(src.pool.checkedin(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=True)  # pragma: no covers
