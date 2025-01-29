import multiprocessing

from fleet_management_api.models import PlatformHW
import fleet_management_api.app as _app
from fleet_management_api.api_impl.auth_controller import (
    generate_test_keys,
    set_auth_params,
    clear_auth_params,
    clear_test_keys,
    get_test_public_key,
)
from fleet_management_api.app import get_token

import tests._utils.api_test as api_test
from fleet_management_http_client_python import ApiClient, Configuration, PlatformHWApi, TenantApi
from fleet_management_http_client_python.exceptions import UnauthorizedException
import time


def stop_app():
    raise RuntimeError("Stopping the app")


class Test_(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()

        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")

        self.app = _app.get_test_app(use_previous=True, predef_api_key="APIKey")
        self.p = multiprocessing.Process(
            target=self.app.run, kwargs={"port": 8080, "debug": False, "use_reloader": False}
        )
        self.p.start()
        time.sleep(1)

    def test_using_correct_api_key_and_specifying_tenant_cookie_allows_to_post_and_read_data(
        self,
    ):
        client = ApiClient(
            configuration=Configuration(
                host="http://localhost:8080/v2/management",
                api_key={"APIKeyAuth": "APIKey"},  # api key
            ),
            cookie="tenant=test-tenant",
        )
        platform_hw_api = PlatformHWApi(client)
        platform_hw_api.create_hws(platform_hw=[PlatformHW(name="test_hw").to_dict()])
        tenant_api = TenantApi(client)
        self.assertEqual([hw.name for hw in platform_hw_api.get_hws()], ["test_hw"])
        self.assertEqual([t.name for t in tenant_api.get_tenants()], ["test-tenant"])

    def test_using_jwt_token_and_cookie_allows_to_post_and_read_data(
        self,
    ):
        token = get_token("test-tenant")
        client = ApiClient(
            configuration=Configuration(
                host="http://localhost:8080/v2/management", access_token=token
            ),
            cookie="tenant=test-tenant",
        )
        platform_hw_api = PlatformHWApi(client)
        response = platform_hw_api.create_hws(platform_hw=[PlatformHW(name="test_hw").to_dict()])
        self.assertEqual([hw.name for hw in response], ["test_hw"])

    def test_posting_data_without_any_authorization_raises_exception(
        self,
    ):
        client = ApiClient(
            configuration=Configuration(host="http://localhost:8080/v2/management"),  # no api key
            cookie="tenant=test-tenant",
        )
        platform_hw_api = PlatformHWApi(client)
        with self.assertRaises(UnauthorizedException):
            platform_hw_api.create_hws(platform_hw=[PlatformHW(name="test").to_dict()])

    def tearDown(self) -> None:
        self.p.terminate()
        self.p.join()
        clear_auth_params()
        clear_test_keys()
