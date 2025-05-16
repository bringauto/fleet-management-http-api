import unittest
import subprocess
import time
import multiprocessing

import psycopg2  # type: ignore
from psycopg2 import OperationalError

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.app import get_app

from tests._utils.constants import TEST_TENANT_NAME
from tests._utils.setup_utils import TenantFromTokenMock


DB_NAME = "test_db"
DOCKER_COMPOSE_FILE_PATH = "tests/_utils/docker-compose.yaml"
# this is only for testing purposes, the password must differ in production
PASSWORD = "1234"


def wait_for_db(max_retries=50, delay=0.1):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME, user="postgres", password=PASSWORD, host="localhost", port=5432
            )
            conn.close()
            print(f"Connection to the test database '{DB_NAME}' has been created.")
            return
        except OperationalError:
            retries += 1
            time.sleep(delay)
    raise TimeoutError("Database did not become available in time")


def restart_database():
    try:
        subprocess.run(["docker", "compose", "-f", DOCKER_COMPOSE_FILE_PATH, "down", "-v"])
        subprocess.run(["docker", "compose", "-f", DOCKER_COMPOSE_FILE_PATH, "up", "-d"])
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
        _connection.set_connection_source("localhost", 5432, "test_db", "postgres", PASSWORD)
        _db_access.add_without_tenant(_db_models.TenantDB(name=TEST_TENANT_NAME))
        self.tenants = TenantFromTokenMock(TEST_TENANT_NAME)

    def _set_up_test_data(self):
        _db_access.add(self.tenants, _db_models.PlatformHWDB(name="platform1"))
        _db_access.add(
            self.tenants, _db_models.CarDB(name="car1", platform_hw_id=1, under_test=True)
        )

    def test_empty_result_is_returned_after_database_is_stopped_and_cleaned_up(self):
        self._set_up_test_data()
        self.assertEqual(_db_access.get(self.tenants, _db_models.CarDB)[0].name, "car1")
        restart_database()

        _db_access.add_tenants(TEST_TENANT_NAME)
        cars = _db_access.get(tenants=self.tenants, base=_db_models.CarDB)
        self.assertFalse(cars)

    def test_object_can_be_added_after_database_cleanup(self):
        restart_database()
        _db_access.add_tenants(TEST_TENANT_NAME)
        self._set_up_test_data()
        self.assertEqual(_db_access.get(self.tenants, _db_models.CarDB)[0].name, "car1")

    def test_deleting_object_after_database_cleanup_fails_but_the_table_exists(self):
        self._set_up_test_data()
        restart_database()
        _db_access.add_tenants(TEST_TENANT_NAME)
        response = _db_access.delete(self.tenants, _db_models.CarDB, id_=1)
        self.assertEqual(response.status_code, 404)

    def test_deleting_n_objects_after_database_cleanup_fails_but_the_table_exists(self):
        self._set_up_test_data()
        _db_access.add(
            self.tenants, _db_models.CarDB(name="car2", platform_hw_id=1, under_test=True)
        )
        _db_access.add(
            self.tenants, _db_models.CarDB(name="car3", platform_hw_id=1, under_test=True)
        )
        restart_database()
        _db_access.add_tenants(TEST_TENANT_NAME)
        response = _db_access.delete_n(
            _db_models.CarDB, n=2, column_name="id", start_from="maximum"
        )
        self.assertEqual(response.body, "0 objects deleted from the database.")

    def test_getting_object_by_id_after_database_cleanup_fails_but_the_table_exists(self):
        self._set_up_test_data()
        restart_database()
        _db_access.add_tenants(TEST_TENANT_NAME)
        response = _db_access.get_by_id(_db_models.CarDB, 1)
        self.assertFalse(response)

    def tearDown(self) -> None:
        try:
            subprocess.run(
                ["docker", "compose", "-f", DOCKER_COMPOSE_FILE_PATH, "down"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error stopping database: {e}")


class Test_Adding_Multiple_Tenants(unittest.TestCase):
    def setUp(self):
        restart_database()
        _connection.set_connection_source("localhost", 5432, "test_db", "postgres", PASSWORD)
        api_key = _db_models.ApiKeyDB(creation_timestamp=0, name="test_key", key="abcde123")
        _db_access.add_without_tenant(api_key)
        self.app = get_app()
        self.p = multiprocessing.Process(
            target=self.app.run, kwargs={"port": 8080, "debug": False, "use_reloader": False}
        )
        self.p.start()

    def test_adding_multiple_tenants_with_non_colliding_names_yield_200_responses(self):
        with self.app.app.test_client() as c:
            response = c.post(
                "/v2/management/tenant?api_key=abcde123", json=[{"name": "test_tenant"}]
            )
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(response.json[0]["name"], "test_tenant")
            self.assertEqual(response.json[0]["id"], 1)

            response = c.post(
                "/v2/management/tenant?api_key=abcde123", json=[{"name": "test_tenant_2"}]
            )
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(response.json[0]["name"], "test_tenant_2")
            self.assertEqual(response.json[0]["id"], 2)

    def tearDown(self) -> None:
        self.p.terminate()
        try:
            subprocess.run(
                ["docker", "compose", "-f", DOCKER_COMPOSE_FILE_PATH, "down"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error stopping database: {e}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
