import unittest
import os
from contextlib import contextmanager

import fleet_management_api.database.connection as _connection
import tests.database.models as models


@contextmanager
def threadpool_test_client(app, tenant=None):
    """Context manager for test_client that avoids Flask 2.2+ context cleanup issues with threading.

    Use this instead of `with app.test_client() as c:` when using ThreadPoolExecutor inside the block.

    Flask's test_client context manager tries to clean up request contexts on exit, which fails
    when those contexts were used by multiple threads. This helper simply yields the client
    without the problematic cleanup - the tests don't rely on session preservation anyway.
    """
    client = app.test_client(tenant) if tenant else app.test_client()
    yield client


class TestCase(unittest.TestCase):

    DEFAULT_TEST_DB_PATH = "test_db.db"

    def setUp(self, test_db_path: str = "", echo_db: bool = False) -> None:
        """This method creates connection and tables for the test database used by the tested Flask server."""
        if not test_db_path:
            test_db_path = self.DEFAULT_TEST_DB_PATH
        self._test_path = test_db_path
        _connection.set_connection_source_test(test_db_path, echo=echo_db)
        models.initialize_test_tables(_connection.current_connection_source())

    def tearDown(self) -> None:  # pragma: no cover
        """This method removes the test database file (sqlite database). If the file does not exist, it prints a message."""
        try:
            if os.path.isfile(self._test_path):
                os.remove(self._test_path)
        except FileNotFoundError:
            print("Cannot delete the test database file. It does not exist.")
        except Exception as e:
            print(f"Error in tearDown method: {e}")
