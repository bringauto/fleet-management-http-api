import unittest
import subprocess
import time

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models


def restart_database():
    subprocess.run(["docker", "compose", "down", "postgresql-database"])
    subprocess.run(["docker", "compose", "up", "postgresql-database", "-d"])
    time.sleep(1.5)


class Test_Database_Cleanup(unittest.TestCase):

    def setUp(self):
        restart_database()
        _connection.set_connection_source("localhost", 5432, "fleet_management_api_db", "postgres", "1234")

    def test_empty_result_is_returned_after_database_is_stopped_and_cleaned_up(self):
        _db_access.add(_db_models.PlatformHWDBModel(name="platform1"))
        _db_access.add(_db_models.CarDBModel(name="car1", platform_hw_id=1, under_test=True))
        self.assertEqual( _db_access.get(_db_models.CarDBModel)[0].name, "car1")
        restart_database()
        cars = _db_access.get(_db_models.CarDBModel)
        self.assertEqual(cars, [])

    def test_object_can_be_added_after_database_cleanup(self):
        restart_database()
        _db_access.add(_db_models.PlatformHWDBModel(name="platform1"))
        _db_access.add(_db_models.CarDBModel(name="car1", platform_hw_id=1, under_test=True))
        self.assertEqual(_db_access.get(_db_models.CarDBModel)[0].name, "car1")

    def test_updating_object_after_database_cleanup_fails_but_the_table_exists(self):
        _db_access.add(_db_models.PlatformHWDBModel(name="platform1"))
        _db_access.add(_db_models.CarDBModel(name="car1", platform_hw_id=1, under_test=True))
        restart_database()
        response = _db_access.update(_db_models.CarDBModel(id=1, name="car1", platform_hw_id=1, under_test=True))
        self.assertEqual(response.status_code, 404)

    def test_deleting_object_after_database_cleanup_fails_but_the_table_exists(self):
        _db_access.add(_db_models.PlatformHWDBModel(name="platform1"))
        _db_access.add(_db_models.CarDBModel(name="car1", platform_hw_id=1, under_test=True))
        restart_database()
        response = _db_access.delete(_db_models.CarDBModel, id_=1)
        self.assertEqual(response.status_code, 404)

    def test_deleting_n_objects_after_database_cleanup_fails_but_the_table_exists(self):
        _db_access.add(_db_models.PlatformHWDBModel(name="platform1"))
        _db_access.add(_db_models.CarDBModel(name="car1", platform_hw_id=1, under_test=True))
        _db_access.add(_db_models.CarDBModel(name="car2", platform_hw_id=1, under_test=True))
        _db_access.add(_db_models.CarDBModel(name="car3", platform_hw_id=1, under_test=True))
        restart_database()
        response = _db_access.delete_n(_db_models.CarDBModel, n=2, column_name="id", start_from="maximum")
        self.assertEqual(response.body, "0 objects deleted from the database.")

    def test_getting_object_by_id_after_database_cleanup_fails_but_the_table_exists(self):
        _db_access.add(_db_models.PlatformHWDBModel(name="platform1"))
        _db_access.add(_db_models.CarDBModel(name="car1", platform_hw_id=1, under_test=True))
        restart_database()
        response = _db_access.get_by_id(_db_models.CarDBModel, 1)
        self.assertEqual(response, [])

    def tearDown(self) -> None:
        subprocess.run(["docker", "compose", "down", "postgresql-database"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
