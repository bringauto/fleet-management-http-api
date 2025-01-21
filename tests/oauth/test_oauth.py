import unittest

import fleet_management_api.app as _app
from fleet_management_api.models import PlatformHW

import tests._utils.api_test as api_test


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
