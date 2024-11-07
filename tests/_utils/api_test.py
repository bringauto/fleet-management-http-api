import unittest
import os

import fleet_management_api.database.connection as _connection
import tests.database.models as models


class TestCase(unittest.TestCase):

    DEFAULT_TEST_DB_PATH = "test_db.db"

    def setUp(self, test_db_path: str = "") -> None:
        if not test_db_path:
            test_db_path = self.DEFAULT_TEST_DB_PATH
        self._test_path = test_db_path
        _connection.set_connection_source_test(test_db_path)
        models.initialize_test_tables(_connection.current_connection_source())

    def tearDown(self) -> None:  # pragma: no cover
        try:
            if os.path.isfile(self._test_path):
                os.remove(self._test_path)
        except FileNotFoundError:
            print("Cannot delete the test database file. It does not exist.")
        except Exception as e:
            print(f"Error in tearDown method: {e}")
