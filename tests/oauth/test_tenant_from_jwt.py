import unittest
from typing import Any


import jwt
import json
from connexion.lifecycle import ConnexionRequest

from fleet_management_api.api_impl.security import (
    NoHeaderWithJWTToken,
    TenantFromToken,
    TenantNotAccessible,
)


TEST_URL = "http://example.com"
TEST_KEY = "key"
TEST_PAYLOAD = {
    "group": [
        "/resources/xx",
    ]
}


def _test_jwt(payload: dict[str, Any]) -> str:
    return jwt.encode(
        {"Payload": json.dumps(payload)},
        TEST_KEY,
        algorithm="HS256",
    )


def _test_auth_header(payload: dict[str, Any]) -> str:
    return f"Bearer {_test_jwt(payload)}"


class Test_Tenant_From_JWT(unittest.TestCase):

    def test_missing_authorization_header_raises_error(self):
        request = ConnexionRequest(TEST_URL, method="GET", headers={})
        with self.assertRaises(NoHeaderWithJWTToken):
            TenantFromToken(request, TEST_KEY)

    def test_tenant_not_set_in_cookies_yields_empty_tenant_name(self):
        request = ConnexionRequest(
            TEST_URL,
            method="GET",
            headers={
                "Authorization": _test_auth_header({"group": ["/customers/test_tenant"]}),
            },
        )
        tenant = TenantFromToken(request, TEST_KEY)
        self.assertEqual(tenant.name, "")

    def test_tenant_in_cookies_matching_tenants_from_jwt_yields_tenant_name(self):
        request = ConnexionRequest(
            TEST_URL,
            method="GET",
            cookies={"tenant": "test_tenant"},
            headers={
                "Authorization": _test_auth_header({"group": ["/customers/test_tenant"]}),
            },
        )
        tenant = TenantFromToken(request, TEST_KEY)
        self.assertEqual(tenant.name, "test_tenant")

    def test_tenant_in_cookies_not_matching_tenants_from_jwt_raises_exception(self):
        request = ConnexionRequest(
            TEST_URL,
            method="GET",
            cookies={"tenant": "inaccessible_tenant"},
            headers={
                "Authorization": _test_auth_header({"group": ["/customers/test_tenant"]}),
            },
        )
        with self.assertRaises(TenantNotAccessible):
            TenantFromToken(request, TEST_KEY)

    def test_tenant_in_cookies_without_any_tenant_in_jwt_token_yields_tenant_name(self) -> None:
        request = ConnexionRequest(
            TEST_URL,
            method="GET",
            cookies={"tenant": "some_tenant"},
            headers={
                "Authorization": _test_auth_header({"group": []}),  # No tenant in JWT token
            },
        )
        tenant = TenantFromToken(request, TEST_KEY)
        self.assertEqual(tenant.name, "some_tenant")

    def test_no_tenant_in_cookies_with_no_tenant_in_jwt_token_yields_empty_tenant_name(
        self,
    ) -> None:
        request = ConnexionRequest(
            TEST_URL,
            method="GET",
            cookies={"tenant": ""},
            headers={
                "Authorization": _test_auth_header({"group": []}),  # No tenant in JWT token
            },
        )
        tenant = TenantFromToken(request, TEST_KEY)
        self.assertEqual(tenant.name, "")

    def test_no_tenant_cookies_with_no_tenant_in_jwt_token_yields_empty_tenant_name(
        self,
    ) -> None:
        request = ConnexionRequest(
            TEST_URL,
            method="GET",
            headers={
                "Authorization": _test_auth_header({"group": []}),  # No tenant in JWT token
            },
        )
        tenant = TenantFromToken(request, TEST_KEY)
        self.assertEqual(tenant.name, "")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
