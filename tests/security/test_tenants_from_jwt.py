import unittest

import jwt

from fleet_management_api.api_impl.auth_controller import (
    generate_test_keys,
    clear_test_keys,
    get_test_public_key,
    set_auth_params,
    clear_auth_params,
)
from fleet_management_api.api_impl.tenants import (
    MissingRSAKey,
    NoHeaderWithJWTToken,
    AccessibleTenants,
    NoAccessibleTenants,
)
from fleet_management_api.app import get_token, get_test_app
from fleet_management_api.models import Tenant
from fleet_management_api.models import PlatformHW
from fleet_management_api.api_impl.load_request import _LoadedRequestEmpty as _RequestEmpty
import tests._utils.api_test as api_test


TEST_URL = "https://example.com"


def testing_auth_header(*tenants: str) -> str:
    token = get_token(*tenants)
    return f"Bearer {token}"


def tenants_from_token(request: _RequestEmpty, key: str, audience: str) -> AccessibleTenants:
    try:
        return AccessibleTenants(request, key, audience)
    except jwt.exceptions.InvalidKeyError:
        print(f"Could not parse key:\n{key}")
        raise


class Test_RSA_Key_Accessibility(unittest.TestCase):

    def setUp(self):
        clear_test_keys()

    def test_not_generatred_rsa_private_key_raises_missing_rsa_key_error(self):
        with self.assertRaises(MissingRSAKey):
            AccessibleTenants(
                _RequestEmpty(
                    TEST_URL,
                    method="GET",
                    headers={"Authorization": testing_auth_header("tenant_x", "tenant_y")},
                ),
                "",
                "account",
            )

    def test_not_set_auth_raises_error(self):
        generate_test_keys()
        with self.assertRaises(MissingRSAKey):
            AccessibleTenants(
                _RequestEmpty(
                    TEST_URL,
                    method="GET",
                    headers={"Authorization": testing_auth_header("tenant_x", "tenant_y")},
                ),
                "",
                "account",
            )

    def test_generated_keys_and_set_auth_params_allow_for_reading_tenants_from_token(self):
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")
        tenants = AccessibleTenants(
            _RequestEmpty(
                TEST_URL,
                method="GET",
                headers={"Authorization": testing_auth_header("tenant_x", "tenant_y")},
            ),
            "",
            "account",
        )
        self.assertEqual(tenants.all, ["tenant_x", "tenant_y"])

    def tearDown(self):
        clear_test_keys()
        clear_auth_params()


class Test_Tenants_From_JWT_Without_API_Key(unittest.TestCase):

    def setUp(self):
        generate_test_keys()

    def test_missing_authorization_header_raises_error(self):
        request = _RequestEmpty(TEST_URL, method="GET", headers={})
        request.headers.pop("Authorization", None)
        # the tenant has to be set in cookies to produce the exception,
        # otherwise an empty tenant name would be returned without exception
        request.cookies["tenant"] = "test_tenant"
        assert "Authorization" not in request.headers
        with self.assertRaises(NoHeaderWithJWTToken):
            AccessibleTenants(request, get_test_public_key(), "account")

    def test_tenant_not_set_in_cookies_yields_empty_tenant_name(self):
        request = _RequestEmpty(
            TEST_URL,
            method="GET",
            headers={
                "Authorization": testing_auth_header("test_tenant"),
            },
        )
        tenant = tenants_from_token(request, get_test_public_key(), "account")
        self.assertEqual(tenant.all, ["test_tenant"])

    def test_tenant_in_cookies_matching_tenants_from_jwt_yields_tenant_name(self):
        request = _RequestEmpty(
            TEST_URL,
            method="GET",
            cookies={"tenant": "test_tenant"},
            headers={"Authorization": testing_auth_header("test_tenant")},
        )
        tenant = AccessibleTenants(request, get_test_public_key(), "account")
        self.assertEqual(tenant.current, "test_tenant")

    def test_tenant_in_cookies_not_matching_tenants_from_jwt_raises_exception(self):
        request = _RequestEmpty(
            TEST_URL,
            method="GET",
            cookies={"tenant": "inaccessible_tenant"},
            headers={
                "Authorization": testing_auth_header("test_tenant"),
            },
        )
        with self.assertRaises(NoAccessibleTenants):
            AccessibleTenants(request, get_test_public_key(), "account")

    def test_tenant_in_cookies_without_any_tenant_in_jwt_token_raises_error(self) -> None:
        request = _RequestEmpty(
            TEST_URL,
            method="GET",
            cookies={"tenant": "some_tenant"},
            headers={
                "Authorization": testing_auth_header(),  # No tenant in JWT token
            },
        )
        with self.assertRaises(NoAccessibleTenants):
            AccessibleTenants(request, get_test_public_key(), "account")

    def test_no_tenant_in_cookies_with_no_tenant_in_jwt_token_raises_error(self) -> None:
        request = _RequestEmpty(
            TEST_URL,
            method="GET",
            cookies={"tenant": ""},
            headers={
                "Authorization": testing_auth_header(),  # No tenant in JWT token
            },
        )
        with self.assertRaises(NoAccessibleTenants):
            AccessibleTenants(request, get_test_public_key(), "account")

    def tearDown(self):
        clear_test_keys()


TEST_TENANT_1 = "test_tenant_1"
TEST_TENANT_2 = "test_tenant_2"
TEST_TENANT_3 = "test_tenant_3"


class Test_Setting_Tenant_Cookie(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")
        self.app = get_test_app(
            "testAPIKey", accessible_tenants=[TEST_TENANT_1, TEST_TENANT_2], use_previous=True
        )
        with self.app.app.test_client() as c:
            c.post(
                "/v2/management/tenant?api_key=testAPIKey",
                json=[
                    Tenant(name=TEST_TENANT_1),
                    Tenant(name=TEST_TENANT_2),
                    Tenant(name=TEST_TENANT_3),
                ],
            )
        with self.app.app.test_client() as client:
            self.hw_1 = PlatformHW(name="test_hw_1")
            client.set_cookie("", "tenant", TEST_TENANT_1)
            client.post("/v2/management/platformhw?api_key=testAPIKey", json=[self.hw_1])
            self.hw_2 = PlatformHW(name="test_hw_2")
            client.set_cookie("", "tenant", TEST_TENANT_2)
            client.post("/v2/management/platformhw?api_key=testAPIKey", json=[self.hw_2])
            self.hw_3 = PlatformHW(name="test_hw_3")
            client.set_cookie("", "tenant", TEST_TENANT_3)
            client.post("/v2/management/platformhw?api_key=testAPIKey", json=[self.hw_3])

    def test_no_api_key_yields_access_only_to_accessible_tenants(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get(
                "/v2/management/platformhw",
                headers={"Authorization": f"Bearer {get_token(TEST_TENANT_1, TEST_TENANT_2)}"},
            )
            assert isinstance(response.json, list)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["name"], self.hw_1.name)
            self.assertEqual(response.json[1]["name"], self.hw_2.name)

    def test_api_key_used_yields_data_for_all_tenants(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/v2/management/platformhw?api_key=testAPIKey")
            self.assertEqual(response.status_code, 200)
            assert isinstance(response.json, list)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["name"], self.hw_1.name)
            self.assertEqual(response.json[1]["name"], self.hw_2.name)
            self.assertEqual(response.json[2]["name"], self.hw_3.name)

    def test_setting_tenant_cookie_yields_data_for_that_tenant_only(self) -> None:
        with self.app.app.test_client() as client:
            client.set_cookie("", "tenant", TEST_TENANT_1)
            response = client.get("/v2/management/platformhw?api_key=testAPIKey")
            self.assertEqual(response.status_code, 200)
            assert isinstance(response.json, list)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["name"], self.hw_1.name)

            client.set_cookie("", "tenant", TEST_TENANT_2)
            response = client.get("/v2/management/platformhw?api_key=testAPIKey")
            self.assertEqual(response.status_code, 200)
            assert isinstance(response.json, list)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["name"], self.hw_2.name)


class Test_Creating_A_Tenant(api_test.TestCase):

    def setUp(self, *args):
        super().setUp()
        self.app = get_test_app("testAPIKey", use_previous=True)

    def test_tenant_is_not_automatically_created_when_posting_new_item(self):
        hw = PlatformHW(name="test_hw_1")
        with self.app.app.test_client() as c:
            c.set_cookie("", "tenant", "other_tenant")
            response = c.post("/v2/management/platformhw?api_key=testAPIKey", json=[hw])
            self.assertEqual(response.status_code, 401)
            # Check that the tenant is not created automatically
            tresponse = c.get("/v2/management/tenant?api_key=testAPIKey")
            self.assertNotIn("other_tenant", [t["name"] for t in tresponse.json])

    def test_creating_nonexistent_tenant_with_valid_api_key_creates_the_tenant(self):
        new_tenant = "new_tenant"
        tenant = Tenant(name=new_tenant)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/tenant?api_key=testAPIKey", json=[tenant])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["name"], new_tenant)

    def test_creating_object_under_new_tenant_after_the_tenant_creation_is_allowed(self):
        hw = PlatformHW(name="test_hw_1")
        name = "new_tenant"
        tenant = Tenant(name=name)
        with self.app.app.test_client() as c:
            c.post("/v2/management/tenant?api_key=testAPIKey", json=[tenant])
            c.set_cookie("", "tenant", name)
            c.post("/v2/management/platformhw?api_key=testAPIKey", json=[hw])
            response = c.get("/v2/management/platformhw?api_key=testAPIKey")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["name"], hw.name)

    def test_creating_new_tenant_without_valid_api_key_yields_401(self):
        new_tenant = "new_tenant"
        tenant = Tenant(name=new_tenant)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/tenant", json=[tenant])
            self.assertEqual(response.status_code, 401)

    def test_creating_tenant_with_already_existing_name_returns_400_error(self):
        new_tenant = "new_tenant"
        tenant = Tenant(name=new_tenant)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/tenant?api_key=testAPIKey", json=[tenant])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["name"], new_tenant)
            # Try to create the same tenant again
            response = c.post("/v2/management/tenant?api_key=testAPIKey", json=[tenant])
            self.assertEqual(response.status_code, 400)

    def test_creating_tenants_with_identical_names_returns_400_error(self):
        name = "new_tenant"
        tenant = Tenant(name=name)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/tenant?api_key=testAPIKey", json=[tenant, tenant])
            self.assertEqual(response.status_code, 400)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
