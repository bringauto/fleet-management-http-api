import unittest

import fleet_management_api.api_impl.security as _secur


class Test_Appending_To_URIs(unittest.TestCase):
    def test_joining_valid_uri_parts(self):
        uri = _secur.appended_uri("http://localhost:8080/api", "v1")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

        uri = _secur.appended_uri("http://localhost:8080/api/", "v1")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

    def test_multiple_slashes_at_the_uri_end_raise_exception(self):
        with self.assertRaises(ValueError):
            _secur.appended_uri("http://localhost:8080/api//", "v1")
        with self.assertRaises(ValueError):
            _secur.appended_uri("http://localhost:8080/api////", "v1")

    def test_slashes_on_the_appended_part_beginning_is_ignored_and_uri_is_composed(
        self,
    ):
        uri = _secur.appended_uri("http://localhost:8080/api", "/v1")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

    def test_slashes_on_the_appended_part_end_is_ignored(self):
        uri = _secur.appended_uri("http://localhost:8080/api", "v1/")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

    def test_appending_multiple_parts(self):
        uri = _secur.appended_uri("http://localhost:8080/api", "v1", "vehicles")
        self.assertEqual(uri, "http://localhost:8080/api/v1/vehicles")

        uri = _secur.appended_uri("http://localhost:8080/api", "v1", "vehicles", "1")
        self.assertEqual(uri, "http://localhost:8080/api/v1/vehicles/1")

        uri = _secur.appended_uri(
            "http://localhost:8080/api/", "/v1", "vehicles/", "/1/", "locations"
        )
        self.assertEqual(uri, "http://localhost:8080/api/v1/vehicles/1/locations")


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
