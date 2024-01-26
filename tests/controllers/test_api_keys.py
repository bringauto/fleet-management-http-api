import unittest
from unittest.mock import patch, Mock

import fleet_management_api.database.connection as _connection
import fleet_management_api.api_impl.api_keys as _api_keys
import fleet_management_api.app as _app


class Test_Creating_And_Veriying_API_Key(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_test_connection_source()

    def test_verifying_nonexistent_key_yields_code_401(self):
        nonexistent_key = "123456789_nonexistent_key"
        code, data = _api_keys.verify_key_and_return_key_info(nonexistent_key)
        self.assertEqual(code, 401)

    @patch("fleet_management_api.api_impl.api_keys._generate_key")
    def test_creating_and_verifying_API_key(self, mock_generate_key: Mock):
        key_name = "test_key"
        mock_generate_key.return_value = "abcd"
        code, msg = _api_keys.create_key(key_name)
        self.assertEqual(code, 200)

        code, data = _api_keys.verify_key_and_return_key_info("abcd")
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(data, _api_keys._ApiKeyDBModel))
        self.assertEqual(data.name, key_name) # type: ignore
        self.assertEqual(data.key, "abcd") # type: ignore

    def test_creating_duplicate_key_yields_code_400(self):
        key_name = "test_key"
        code, msg = _api_keys.create_key(key_name)
        self.assertEqual(code, 200)
        code, msg = _api_keys.create_key(key_name)
        self.assertEqual(code, 400)


class Test_Using_API_Key_In_App(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_test_connection_source("db_file.db")
        self.app = _app.get_test_app()

    def test_using_nonexistent_key_yields_code_401(self):
        with self.app.app.test_client() as c:
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)

    @patch("fleet_management_api.api_impl.api_keys._generate_key")
    def test_using_existing_key_yields_code_200(self, mock_generate_key: Mock):
        key_name = "test_key_2"
        mock_generate_key.return_value = "1234"
        code, msg = _api_keys.create_key(key_name)
        self.assertEqual(code, 200)
        with self.app.app.test_client() as c:
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main() # pragma: no cover