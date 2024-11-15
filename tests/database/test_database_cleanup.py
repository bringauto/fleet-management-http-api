import unittest
import subprocess
import time
import psycopg2  # type: ignore
from psycopg2 import OperationalError

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
from tests._utils import TEST_TENANT


def wait_for_db(max_retries=50, delay=0.1):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                dbname="test_management_api",
                user="postgres",
                password="1234",
                host="localhost",
                port=5432,
            )
            conn.close()
            return
        except OperationalError:
            retries += 1
            time.sleep(delay)
    raise TimeoutError("Database did not become available in time")


def restart_database():
    try:
        subprocess.run(["docker", "compose", "down", "postgresql-database"])
        subprocess.run(["docker", "compose", "up", "postgresql-database", "-d"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart database: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error when restarting database connection: {e}")
        raise
    wait_for_db()


class Test_Database_Cleanup(unittest.TestCase):

    def setUp(self):
        restart_database()
        _connection.set_connection_source(
            "localhost", 5432, "test_management_api", "postgres", "1234"
        )

    def _set_up_test_data(self):
        _db_access.add(TEST_TENANT, _db_models.PlatformHWDBModel(name="platform1"))
        _db_access.add(
            TEST_TENANT, _db_models.CarDBModel(name="car1", platform_hw_id=1, under_test=True)
        )

    def test_empty_result_is_returned_after_database_is_stopped_and_cleaned_up(self):
        self._set_up_test_data()
        self.assertEqual(_db_access.get(_db_models.CarDBModel)[0].name, "car1")
        restart_database()
        cars = _db_access.get(TEST_TENANT, _db_models.CarDBModel)
        self.assertFalse(cars)

    def test_object_can_be_added_after_database_cleanup(self):
        restart_database()
        self._set_up_test_data()
        self.assertEqual(_db_access.get(_db_models.CarDBModel)[0].name, "car1")

    def test_deleting_object_after_database_cleanup_fails_but_the_table_exists(self):
        self._set_up_test_data()
        restart_database()
        response = _db_access.delete(TEST_TENANT, _db_models.CarDBModel, id_=1)
        self.assertEqual(response.status_code, 404)

    def test_deleting_n_objects_after_database_cleanup_fails_but_the_table_exists(self):
        self._set_up_test_data()
        _db_access.add(
            TEST_TENANT, _db_models.CarDBModel(name="car2", platform_hw_id=1, under_test=True)
        )
        _db_access.add(
            TEST_TENANT, _db_models.CarDBModel(name="car3", platform_hw_id=1, under_test=True)
        )
        restart_database()
        response = _db_access.delete_n(
            TEST_TENANT, _db_models.CarDBModel, n=2, column_name="id", start_from="maximum"
        )
        self.assertEqual(response.body, "0 objects deleted from the database.")

    def test_getting_object_by_id_after_database_cleanup_fails_but_the_table_exists(self):
        self._set_up_test_data()
        restart_database()
        response = _db_access.get_by_id(TEST_TENANT, _db_models.CarDBModel, 1)
        self.assertFalse(response)

    def tearDown(self) -> None:
        try:
            subprocess.run(["docker", "compose", "down", "postgresql-database"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error stopping database: {e}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
