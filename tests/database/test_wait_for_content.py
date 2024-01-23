import unittest
import sys
sys.path.append('.')
import os
from concurrent.futures import ThreadPoolExecutor

import fleet_management_api.database.connection as connection
import fleet_management_api.database.db_access as db_access
import tests.database.models as models


_TEST_DB_FILE_PATH = "test.db"


class Test_Waiting_For_Content(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source(_TEST_DB_FILE_PATH)
        models.initialize_test_tables(connection.current_connection_source())

    def test_waiting_for_content(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(db_access.get_records, models.TestBase, wait=True)
            executor.submit(db_access.add_record, models.TestBase, models.TestBase(id=5, test_str="test", test_int=123))
            retrieved_objs = future.result()
            self.assertEqual(len(retrieved_objs), 1)

    def tearDown(self) -> None:
        if os.path.isfile(_TEST_DB_FILE_PATH):
            os.remove(_TEST_DB_FILE_PATH)


if __name__=="__main__":
    unittest.main() # pragma: no covers