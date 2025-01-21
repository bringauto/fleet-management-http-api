import unittest
import os

import fleet_management_api.api_impl.security as _security
import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import PlatformHW

import tests._utils.api_test as api_test
from tests._utils.constants import TEST_TENANT_NAME


class Test_Appending_To_URIs(unittest.TestCase):
    def test_joining_valid_uri_parts(self):
        uri = _security.appended_uri("http://localhost:8080/api", "v1")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

        uri = _security.appended_uri("http://localhost:8080/api/", "v1")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

    def test_multiple_slashes_at_the_uri_end_raise_exception(self):
        with self.assertRaises(ValueError):
            _security.appended_uri("http://localhost:8080/api//", "v1")
        with self.assertRaises(ValueError):
            _security.appended_uri("http://localhost:8080/api////", "v1")

    def test_slashes_on_the_appended_part_beginning_is_ignored_and_uri_is_composed(
        self,
    ):
        uri = _security.appended_uri("http://localhost:8080/api", "/v1")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

    def test_slashes_on_the_appended_part_end_is_ignored(self):
        uri = _security.appended_uri("http://localhost:8080/api", "v1/")
        self.assertEqual(uri, "http://localhost:8080/api/v1")

    def test_appending_multiple_parts(self):
        uri = _security.appended_uri("http://localhost:8080/api", "v1", "vehicles")
        self.assertEqual(uri, "http://localhost:8080/api/v1/vehicles")

        uri = _security.appended_uri("http://localhost:8080/api", "v1", "vehicles", "1")
        self.assertEqual(uri, "http://localhost:8080/api/v1/vehicles/1")

        uri = _security.appended_uri(
            "http://localhost:8080/api/", "/v1", "vehicles/", "/1/", "locations"
        )
        self.assertEqual(uri, "http://localhost:8080/api/v1/vehicles/1/locations")


class Test_Playing_With_Oauth(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("db_file.db")
        self.app = _app.get_test_app(predef_api_key="key_not_used")

    def _test_using_nonexistent_key_yields_code_401(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get(
                "/v2/management/car",
                headers={
                    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJJMzUxbWE2TkVBcW5JTlBYalV5OVlpTVVWUk15SlNoUUtWd2xENWl1UXpvIn0.eyJleHAiOjE3MzE1ODEyMDksImlhdCI6MTczMTU4MDkwOSwiYXV0aF90aW1lIjoxNzMxNTgwOTA4LCJqdGkiOiJhMzViYWQ4NC1kMDU4LTQyNzctODYyZS0wOTg0NDY4NTlmZGQiLCJpc3MiOiJodHRwczovL2tleWNsb2FrLmJyaW5nYXV0by5jb20vcmVhbG1zL2JyaW5nYXV0byIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJmNmRkZWQ1MS1hOTAzLTRhOWUtYjJmOS02NTMxMmYwYmRmYTIiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhcGkuZGV2LmJyaW5nYXV0b2ZsZWV0LmNvbSIsIm5vbmNlIjoiIiwic2Vzc2lvbl9zdGF0ZSI6ImQyODdlY2EzLWM2YmEtNGQxNS05YjcwLTU5ZmM5Y2M5MTAzNyIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9hcGkuZGV2LmJyaW5nYXV0b2ZsZWV0LmNvbSIsImh0dHBzOi8vYXBwLmFwcHNtaXRoLmNvbSIsImh0dHBzOi8vYXBwc21pdGguZGV2LmJyaW5nYXV0b2ZsZWV0LmNvbSIsImh0dHBzOi8vb2F1dGgucmV0b29sLmNvbSIsImFwaS5kZXYuYnJpbmdhdXRvZmxlZXQuY29tIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLWJyaW5nYXV0byIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Ik1hcEdyb3VwcyBwcm9maWxlIGVtYWlsIiwic2lkIjoiZDI4N2VjYTMtYzZiYS00ZDE1LTliNzAtNTlmYzljYzkxMDM3IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoidCB0IiwicHJlZmVycmVkX3VzZXJuYW1lIjoidGVzIiwiZ2l2ZW5fbmFtZSI6InQiLCJmYW1pbHlfbmFtZSI6InQiLCJlbWFpbCI6InRlc0BicmluZ2F1dG8uY29tIiwiZ3JvdXAiOlsiL2N1c3RvbWVycy9icmluZ2F1dG8iLCIvcmVzb3VyY2VzL2RldmVsb3BtZW50L2ZsZWV0LXByb3RvY29sLWh0dHAtYXBpL2NhcnMiLCIvcmVzb3VyY2VzL2RldmVsb3BtZW50L2ZsZWV0LXByb3RvY29sLWh0dHAtYXBpIl19.lY9kA8VcbwyTjZFu-a7Ke86-8LkNYbNQAJjzfEXtNl1dhDUI7wO2K7gTUDh6Ev4wluo9NSDEanNQb0pR1B0MAzP7IOxqEk1WuuHsXaHoYb8Ncsj4g47T8y3Q7c4FJ1VMtcnqYb46mIzIytS7dMnsADt3pRQpA5MpZTSCyjv1N6-Kfc35UHyd6uwKl-6O7Iv7ryZ6EmztRYEBsM0t6Vyb2DUj0j4mTw03fAlra3I0YFHQcsSItOpYmcpciRVN65G_K44qCEEXrLh-CEHyk2sKUDYitUV-czQmWpE6JKHMnmI2TeXpdGPoGJmpRcUPsdB1BXq40RNY9Jgz2e3dnGhriA"
                },
            )
            print(response.json)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("db_file.db"):
            os.remove("db_file.db")


TEST_TOKEN_HEADER = {"alg": "RS256", "typ": "JWT", "kid": "test"}
TEST_TOKEN_PAYLOAD = {
    "exp": 1000,
    "iat": 1000,
    "auth_time": 1000,
    "jti": "",
    "iss": "",
    "aud": "",
    "sub": "",
    "typ": "Bearer",
    "azp": "",
    "nonce": "",
    "session_state": "",
    "acr": "1",
    "allowed-origins": [],
    "realm_access": {"roles": ["", "offline_access", "uma_authorization"]},
    "resource_access": {
        "account": {"roles": ["manage-account", "manage-account-links", "view-profile"]}
    },
    "scope": "",
    "sid": "",
    "email_verified": False,
    "name": "",
    "preferred_username": "",
    "given_name": "",
    "family_name": "",
    "email": "",
    "group": [],
}
TEST_TOKEN = {"Header": TEST_TOKEN_HEADER, "Payload": TEST_TOKEN_PAYLOAD, "Signature": {}}


TEST_TENANT_1 = "test_tenant_1"
TEST_TENANT_2 = "test_tenant_2"


class Test_Setting_Tenant_Cookie(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app("testKey", tenants=[TEST_TENANT_1, TEST_TENANT_2])
        with self.app.app.test_client() as client:
            self.hw_1 = PlatformHW(name="test_hw_1")
            client.set_cookie("", "tenant", TEST_TENANT_1)
            client.post("/v2/management/platformhw?api_key=testKey", json=[self.hw_1])
            self.hw_2 = PlatformHW(name="test_hw_2")
            client.set_cookie("", "tenant", TEST_TENANT_2)
            client.post("/v2/management/platformhw?api_key=testKey", json=[self.hw_2])

    def test_no_api_key_authentication_yields_401_response(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/v2/management/platformhw")
            self.assertEqual(response.status_code, 401)

    def test_api_key_used_returns_data_for_all_tenants(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/v2/management/platformhw?api_key=testKey")
            self.assertEqual(response.status_code, 200)
            assert isinstance(response.json, list)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["name"], self.hw_1.name)
            self.assertEqual(response.json[1]["name"], self.hw_2.name)

    def test_for_given_tenant_yields_data_for_that_tenant_only(self) -> None:
        with self.app.app.test_client() as client:
            client.set_cookie("", "tenant", TEST_TENANT_1)
            response = client.get("/v2/management/platformhw?api_key=testKey")
            self.assertEqual(response.status_code, 200)
            assert isinstance(response.json, list)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["name"], self.hw_1.name)

            client.set_cookie("", "tenant", TEST_TENANT_2)
            response = client.get("/v2/management/platformhw?api_key=testKey")
            self.assertEqual(response.status_code, 200)
            assert isinstance(response.json, list)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["name"], self.hw_2.name)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
