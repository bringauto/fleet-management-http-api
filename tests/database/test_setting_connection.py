import os
import unittest
from unittest.mock import patch, Mock
import sys

sys.path.append(".")

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.script_args as _args
import fleet_management_api.database.db_models as _db_models
from tests.database.models import TestBase as _TestBase  # type: ignore
from tests.database.models import initialize_test_tables as _initialize_test_tables


class Test_Creating_Database_URL(unittest.TestCase):
    def test_production_database_url_with_specified_port_username_and_password(self):
        url = _connection.db_url("test_user", "test_password", "localhost", 5432, "test_db")
        self.assertEqual(url, "postgresql+psycopg://test_user:test_password@localhost:5432/test_db")

    def test_production_database_url_with_specified_username_and_password(self):
        url = _connection.db_url("test_user", "test_password", "localhost", db_name="test_db")
        self.assertEqual(url, "postgresql+psycopg://test_user:test_password@localhost/test_db")

    def test_production_database_url_without_username_and_password(self):
        url = _connection.db_url(location="localhost", db_name="test_db")
        self.assertEqual(url, "postgresql+psycopg://localhost/test_db")

    def test_production_database_url_without_specifying_database_name_gives_valid_url(
        self,
    ):
        url = _connection.db_url("test_user", "test_password", "localhost")
        self.assertEqual(url, "postgresql+psycopg://test_user:test_password@localhost")

    def test_test_database_url(self):
        url = _connection.db_url_test()
        self.assertEqual(url, "sqlite:///:memory:")

    def test_test_database_url_with_specified_file_location(self):
        url = _connection.db_url_test("test_db_file")
        self.assertEqual(url, "sqlite:///test_db_file")

    def test_value_error_is_raises_when_specifying_password_without_username(self):
        with self.assertRaises(ValueError):
            _connection.db_url(
                location="localhost",
                db_name="test_db",
                password="test_password",
                username="",
            )


class Test_Creating_A_Test_Database(unittest.TestCase):
    def setUp(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db_file.db"):
            os.remove("test_db_file.db")

    def test_setting_up_a_test_database(self):
        db_file_path = os.path.abspath("test_db_file.db")
        _connection.set_connection_source_test("test_db_file.db")
        self.assertTrue(os.path.isfile(db_file_path))

    def test_test_database_file_is_always_removed_and_created_anew_when_setting_new_test_connection_using_the_same_file(
        self,
    ):
        _connection.set_connection_source_test("test_db_file.db")
        _initialize_test_tables(_connection.current_connection_source())
        test_obj = _TestBase(id=1, test_str="test_name", test_int=1)
        response = _db_access.add(test_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(_db_access.get(_TestBase)), 1)

        _connection.set_connection_source_test("test_db_file.db")
        _initialize_test_tables(_connection.current_connection_source())

        self.assertEqual(len(_db_access.get(_TestBase)), 0)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db_file.db"):
            os.remove("test_db_file.db")


class Test_Initializing_Tables(unittest.TestCase):
    def test_initializing_tables_without_connection_being_set_raises_exception(self):
        _connection.unset_connection_source()
        with self.assertRaises(RuntimeError):
            _initialize_test_tables(_connection.current_connection_source())


class Test_Setting_Up_Database(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_connection_source = _connection.current_connection_source()
        _connection.set_connection_source_test("test_db_file.db")

    @patch("fleet_management_api.database.connection._set_connection")
    def test_setting_max_number_of_table_rows(self, mock_settting_connection: Mock):
        _connection.set_up_database(
            _args.Database(
                connection=_args.Database.Connection(
                    location="test_db_file.db",
                    database_name="test_db",
                    username="test_user",
                    password="test_password",
                    port=5432,
                ),
                maximum_number_of_table_rows={"car_states": 18, "order_states": 124},
            )
        )
        self.assertEqual(_db_models.CarStateDBModel.max_n_of_stored_states(), 18)
        self.assertEqual(_db_models.OrderStateDBModel.max_n_of_stored_states(), 124)

    @patch("fleet_management_api.database.connection._set_connection")
    def test_setting_up_database_without_connection_being_set_raises_exception(
        self, mock_settting_connection: Mock
    ):
        _connection.unset_connection_source()
        with self.assertRaises(RuntimeError):
            _connection.set_up_database(
                _args.Database(
                    connection=_args.Database.Connection(
                        location="test_db_file.db",
                        database_name="test_db",
                        username="test_user",
                        password="test_password",
                        port=5432,
                    ),
                    maximum_number_of_table_rows={
                        "car_states": 18,
                        "order_states": 124,
                    },
                )
            )

    def tearDown(self) -> None:  # pragma: no cover
        _connection.replace_connection_source(self._orig_connection_source)
        if os.path.isfile("test_db_file.db"):
            os.remove("test_db_file.db")


class Test_Calling_DB_Access_Methods_Without_Setting_Connection(unittest.TestCase):
    def test_calling_add_method_without_setting_connection_raises_runtime_error(self):
        _connection.unset_connection_source()
        self.assertTrue(_connection.current_connection_source() is None)
        test_obj = _TestBase(id=1, test_str="test_name", test_int=1)
        with self.assertRaises(RuntimeError):
            _db_access.add(test_obj)


class Test_Getting_Connection_Source_As_A_Variable(unittest.TestCase):
    def test_getting_connection_source_does_not_set_current_connection_source_in_connection_module(
        self,
    ):
        source_1 = _connection.get_connection_source_test("test_db_file.db")
        source_2 = _connection.current_connection_source()
        self.assertTrue(source_1 is not None)
        self.assertFalse(source_1 is source_2)
        self.assertTrue(source_2 is not None)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db_file.db"):
            os.remove("test_db_file.db")


class Test_Failed_Connection(unittest.TestCase):
    @patch("fleet_management_api.database.db_models.Base.metadata.create_all")
    @patch("fleet_management_api.database.connection._test_new_connection")
    def test_invalid_connection_source(self, mock_test_new_connection: Mock, create_all: Mock):
        _connection.set_connection_source(
            db_location="localhost",
            port=1111,
            username="invalid_name",
            password="invalid_password",
            db_name="test_db",
        )
        self.assertFalse(_connection.is_connected_to_database())


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no cover
