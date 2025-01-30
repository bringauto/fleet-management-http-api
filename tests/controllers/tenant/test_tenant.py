import unittest

import fleet_management_api.app as _app
from fleet_management_api.database.connection import (
    set_connection_source_test,
)
from fleet_management_api.database.db_access import add_tenants
from fleet_management_api.models import Tenant
from fleet_management_api.api_impl.auth_controller import (
    generate_test_keys,
    set_auth_params,
    get_test_public_key,
)
from fleet_management_api.app import get_token


class Test_Get_Tenants(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True, predef_api_key="test_key")
        add_tenants("tenant_1", "tenant_2", "tenant_3")

    def test_api_key_yields_all_existing_tenants(self) -> None:
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/tenant?api_key=test_key")
            assert response.json is not None
            tenants: list[Tenant] = [Tenant(**t) for t in response.json]
            self.assertEqual([t.name for t in tenants], ["tenant_1", "tenant_2", "tenant_3"])

    def test_jwt_token_yields_only_accessible_tenants(self) -> None:
        generate_test_keys()
        set_auth_params(public_key=get_test_public_key(strip=True), client_id="test_client")
        with self.app.app.test_client() as c:
            response = c.get(
                "/v2/management/tenant",
                headers={"Authorization": f"Bearer {get_token('tenant_1', 'tenant_2')}"},
            )
            assert response.json is not None
            tenants: list[Tenant] = [Tenant(**t) for t in response.json]
            self.assertEqual([t.name for t in tenants], ["tenant_1", "tenant_2"])


class Test_Setting_Tenant_Cookie(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True, predef_api_key="test_key")
        add_tenants("tenant_1", "tenant_2", "tenant_3")

    def test_using_id_of_nonexistent_tenant_yields_404_error(self) -> None:
        with self.app.app.test_client() as c:
            tenant_id = 1543543453
            response = c.head(f"/v2/management/tenant/{tenant_id}?api_key=test_key")
            self.assertEqual(response.status_code, 404)
            self.assertNotIn("Set-Cookie", response.headers)

    def test_using_id_of_existing_tenant_yields_200_code_and_sets_cookie(self) -> None:
        with self.app.app.test_client() as c:
            tenant_id = 1
            response = c.head(f"/v2/management/tenant/{tenant_id}?api_key=test_key")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Set-Cookie", response.headers)
            self.assertEqual(response.headers["Set-Cooke"], f"tenant={tenant_id}")

            tenant_id = 2
            response = c.head(f"/v2/management/tenant/{tenant_id}?api_key=test_key")
            self.assertEqual(response.headers["Set-Cookie"], f"tenant={tenant_id}")

    def test_using_id_of_existing_but_inaccessible_tenant_yields_401_code_and_does_not_set_cookie(
        self,
    ):
        generate_test_keys()
        set_auth_params(public_key=get_test_public_key(strip=True), client_id="test_client")
        with self.app.app.test_client() as c:
            tenant_id = 1  # id of tenant_1, that is not included in the JWT token
            response = c.head(
                f"/v2/management/tenant/{tenant_id}",
                headers={"Authorization": f"Bearer {get_token('tenant_2', 'tenant_3')}"},
            )
            self.assertEqual(response.status_code, 401)
            self.assertNotIn("Set-Cookie", response.headers)


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no coverages
