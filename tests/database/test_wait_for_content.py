import unittest
import sys
sys.path.append('.')
import os
from concurrent.futures import ThreadPoolExecutor
import time

import fleet_management_api.database.connection as connection
import fleet_management_api.database.db_access as db_access
import tests.database.models as models


_TEST_DB_FILE_PATH = "test_db_file.db"


class Test_Waiting_For_Content(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source(_TEST_DB_FILE_PATH)
        models.initialize_test_tables(connection.current_connection_source())

    def test_enabling_wait_mechanism_when_no_content_is_available_makes_the_db_request_wait_for_available_content_and_to_return_nonempty_list(self):
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

    def tearDown(self) -> None:
        if os.path.isfile(_TEST_DB_FILE_PATH):
            os.remove(_TEST_DB_FILE_PATH)


if __name__=="__main__":
    unittest.main() # pragma: no covers