import unittest
from unittest.mock import patch, Mock

import fleet_management_api.app as _app
from fleet_management_api.database.connection import (
    set_connection_source_test,
    unset_connection_source,
)
from tests._utils.constants import TEST_TENANT_NAME


class Test_API_Checking(unittest.TestCase):
    def test_unavailable_api_yields_code_404(self):
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.head("/nonexistent-base/apialive")
            self.assertEqual(response.status_code, 404)

    def test_available_api_yields_code_200(self):
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.head("/v2/management/apialive")
            self.assertEqual(response.status_code, 200)

    @patch("fleet_management_api.controllers.security_controller.info_from_APIKeyAuth")
    def test_missing_database_connection_in_middle_of_request_yields_code_503(
        self, mock_info_from_APIKeyAuth: Mock
    ):
        set_connection_source_test()
        mock_info_from_APIKeyAuth.return_value = {"name": "Admin"}
        self.app = _app.get_test_app(use_previous=True)
        unset_connection_source()
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.head("/v2/management/apialive")
            self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
