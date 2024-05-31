import os
import unittest

import pydantic

from fleet_management_api.script_args.args import load_config_file
import fleet_management_api.script_args.configs as _configs


_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class Test_Whole_Config(unittest.TestCase):
    def setUp(self) -> None:
        self.config_dict = load_config_file(os.path.join(_CURRENT_DIR, "./test_config.json"))

    def test_loading_config_dict_with_all_required_fields(self):
        _configs.APIConfig(**self.config_dict)


class Test_HTTP_Server_Config(unittest.TestCase):
    def setUp(self) -> None:
        main_config = load_config_file(os.path.join(_CURRENT_DIR, "./test_config.json"))
        self.config_dict = main_config["http_server"]

    def test_loading_http_server_config(self):
        config_obj = _configs.HTTPServer(**self.config_dict)
        self.assertEqual(str(config_obj.base_uri), self.config_dict["base_uri"])

    def test_raise_error_when_http_server_base_uri_is_invalid(self):
        self.config_dict["base_uri"] = ""
        with self.assertRaises(pydantic.ValidationError):
            _configs.HTTPServer(**self.config_dict)
        self.config_dict["base_uri"] = "http://"
        with self.assertRaises(pydantic.ValidationError):
            _configs.HTTPServer(**self.config_dict)

    def test_raise_error_when_data_is_missing(self):
        for key in self.config_dict.keys():
            with self.subTest(key=key):
                invalid_config_dict = self.config_dict.copy()
                invalid_config_dict.pop(key)
                with self.assertRaises(pydantic.ValidationError):
                    _configs.APIConfig(**invalid_config_dict)


class Test_Database_Config(unittest.TestCase):
    def setUp(self) -> None:
        main_config = load_config_file(os.path.join(_CURRENT_DIR, "./test_config.json"))
        self.config_dict = main_config["database"]

    def test_loading_database_config(self):
        config_obj = _configs.Database(**self.config_dict)
        self.assertEqual(config_obj.connection.model_dump(), self.config_dict["connection"])
        self.assertEqual(
            config_obj.maximum_number_of_table_rows,
            self.config_dict["maximum_number_of_table_rows"],
        )

    def test_raise_error_when_maximum_number_of_table_rows_are_missing(self):
        self.config_dict.pop("maximum_number_of_table_rows")
        with self.assertRaises(pydantic.ValidationError):
            _configs.Database(**self.config_dict)

    def test_raise_error_when_database_connection_is_missing(self):
        self.config_dict.pop("connection")
        with self.assertRaises(pydantic.ValidationError):
            _configs.Database(**self.config_dict)

    def test_raise_exception_on_empty_database_connection_location(self):
        self.config_dict["connection"]["location"] = ""
        with self.assertRaises(pydantic.ValidationError):
            _configs.Database(**self.config_dict)

    def test_allow_empty_username_and_password(self):
        self.config_dict["connection"]["username"] = ""
        self.config_dict["connection"]["password"] = ""
        _configs.Database(**self.config_dict)

    def test_maximum_number_of_table_rows_must_be_at_least_one(self):
        self.config_dict["maximum_number_of_table_rows"]["test_table_1"] = 0
        self.config_dict["maximum_number_of_table_rows"]["test_table_2"] = 0
        with self.assertRaises(pydantic.ValidationError):
            _configs.Database(**self.config_dict)
        self.config_dict["maximum_number_of_table_rows"]["test_table_2"] = -5
        with self.assertRaises(pydantic.ValidationError):
            _configs.Database(**self.config_dict)


class Test_Security_Config(unittest.TestCase):
    def setUp(self) -> None:
        main_config = load_config_file(os.path.join(_CURRENT_DIR, "./test_config.json"))
        self.config_dict = main_config["security"]

    def test_loading_security_config(self):
        config_obj = _configs.Security(**self.config_dict)
        self.assertEqual(str(config_obj.keycloak_url), self.config_dict["keycloak_url"])
        self.assertEqual(config_obj.client_id, self.config_dict["client_id"])
        self.assertEqual(config_obj.client_secret_key, self.config_dict["client_secret_key"])
        self.assertEqual(config_obj.scope, self.config_dict["scope"])
        self.assertEqual(config_obj.realm, self.config_dict["realm"])

    def test_raise_error_when_data_is_missing(self):
        for key in self.config_dict.keys():
            with self.subTest(key=key):
                invalid_config_dict = self.config_dict.copy()
                invalid_config_dict.pop(key)
                with self.assertRaises(pydantic.ValidationError):
                    _configs.Security(**invalid_config_dict)


class Test_API_Config(unittest.TestCase):
    def setUp(self) -> None:
        main_config = load_config_file(os.path.join(_CURRENT_DIR, "./test_config.json"))
        self.config_dict = main_config["api"]

    def test_loading_api_config(self):
        config_obj = _configs.API(**self.config_dict)
        self.assertEqual(
            config_obj.request_for_data.timeout_in_seconds,
            self.config_dict["request_for_data"]["timeout_in_seconds"],
        )

    def test_raise_error_when_request_for_data_is_missing(self):
        self.config_dict.pop("request_for_data")
        with self.assertRaises(pydantic.ValidationError):
            _configs.API(**self.config_dict)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
