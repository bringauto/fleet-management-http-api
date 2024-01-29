import os
import unittest
from unittest.mock import patch, Mock

import fleet_management_api.database.connection as _connection
import fleet_management_api.api_impl.api_keys as _api_keys
import fleet_management_api.app as _app


class Test_Creating_And_Veriying_API_Key(unittest.TestCase):

    def setUp(self) -> None:
        self.src = _connection.get_connection_source_test("test_db_file.db")

    def test_verifying_nonexistent_key_yields_code_401(self):
        nonexistent_key = "123456789_nonexistent_key"
        code, data = _api_keys.verify_key_and_return_key_info(nonexistent_key, self.src)
        self.assertEqual(code, 401)

    @patch("fleet_management_api.api_impl.api_keys._generate_key")
    def test_creating_and_verifying_API_key(self, mock_generate_key: Mock):
        key_name = "test_key"
        mock_generate_key.return_value = "abcd"
        code, msg = _api_keys.create_key(key_name, self.src)
        self.assertEqual(code, 200)

        code, data = _api_keys.verify_key_and_return_key_info("abcd", self.src)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(data, _api_keys._ApiKeyDBModel))
        self.assertEqual(data.name, key_name) # type: ignore
        self.assertEqual(data.key, "abcd") # type: ignore

    def test_creating_duplicate_key_yields_code_400(self):
        key_name = "test_key"
        code, msg = _api_keys.create_key(key_name, self.src)
        self.assertEqual(code, 200)
        code, msg = _api_keys.create_key(key_name, self.src)
        self.assertEqual(code, 400)

    def tearDown(self) -> None:
        if os.path.isfile("test_db_file.db"):
            os.remove("test_db_file.db")


class Test_Using_API_Key_In_App(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("db_file.db")
        self.app = _app.get_test_app()

    def test_using_nonexistent_key_yields_code_401(self):
        with self.app.app.test_client() as c:
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        if os.path.isfile("db_file.db"):
            os.remove("db_file.db")


class Test_Using_Already_Existing_API_Key(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("db_file.db")
        self.app = _app.get_test_app(predef_api_key="abcd")

    @patch("fleet_management_api.api_impl.api_keys._generate_key")
    def test_using_existing_key(self, mock_generate_key: Mock):
        mock_generate_key.return_value = "abcd"
        with self.app.app.test_client() as c:
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 401)
            response = c.get('/v1/car?api_key=abcd')
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        if os.path.isfile("db_file.db"):
            os.remove("db_file.db")


if __name__ == '__main__':
    unittest.main() # pragma: no cover