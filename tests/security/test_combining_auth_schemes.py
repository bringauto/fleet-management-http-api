import unittest

from connexion.exceptions import Unauthorized
from fleet_management_api.app import get_test_app, get_token
from fleet_management_api.api_impl.auth_controller import (
    set_auth_params,
    generate_test_keys,
    get_test_public_key,
)
import tests._utils.api_test as api_test


class Test_Combining_Security_Schemes(api_test.TestCase):

    def setUp(self):
        super().setUp()
        self.app = get_test_app(predef_api_key="test_key")
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")

    def test_passing_jwt_token_and_api_key_simultaneously_yields_401_code(self):
        with self.app.app.test_client() as c:
            # Get a JWT token
            jwt_token = get_token("tenant_1")
            # Make a request with both the JWT token and API key
            response = c.get(
                "/v2/management/car?api_key=test_key",
                headers={"Authorization": f"Bearer {jwt_token}"},
            )
            self.assertEqual(response.status_code, 401)
            self.assertIn("JWT token", response.json["detail"])
            self.assertIn("API key", response.json["detail"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
