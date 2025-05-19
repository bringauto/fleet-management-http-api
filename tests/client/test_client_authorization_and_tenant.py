import multiprocessing
import time
import unittest

import fleet_management_api.app as _app
from fleet_management_api.api_impl.auth_controller import (
    generate_test_keys,
    set_auth_params,
    clear_auth_params,
    clear_test_keys,
    get_test_public_key,
)
from fleet_management_api.app import get_token, TestApp
from fleet_management_http_client_python import (
    ApiClient,
    Configuration,
    PlatformHWApi,
    TenantApi,
    ApiApi,
)
from fleet_management_http_client_python.exceptions import UnauthorizedException
from fleet_management_http_client_python.models import PlatformHW as PlatformHWFor

import tests._utils.api_test as api_test


def stop_app():
    raise RuntimeError("Stopping the app")


def wait_for_process(app: TestApp, process: multiprocessing.Process, timeout: float = 10):
    process.start()
    retry_interval = 1
    start = time.time()
    host = "http://localhost:8080/v2/management"
    client = ApiClient(
        configuration=Configuration(host=host, api_key={"APIKeyAuth": "APIKey"}),
        cookie="tenant=test-tenant",
    )
    api_api = ApiApi(client)
    while time.time() - start < timeout:
        try:
            api_api.check_api_is_alive()
            break
        except Exception as e:
            # Log the error for debugging
            print(f"Server not ready: {e}")
            time.sleep(retry_interval)
    else:
        process.terminate()
        raise RuntimeError("Failed to start test server")


class Test_Authorization(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()

        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")

        self.app = _app.get_test_app(use_previous=True, predef_api_key="APIKey")
        self.p = multiprocessing.Process(
            target=self.app.run, kwargs={"port": 8080, "debug": False, "use_reloader": False}
        )
        wait_for_process(self.app, self.p)

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
        platform_hw_api.create_hws(platform_hw=[PlatformHWFor(name="test_hw")])
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
        response = platform_hw_api.create_hws(platform_hw=[PlatformHWFor(name="test_hw")])
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
            platform_hw_api.create_hws(platform_hw=[PlatformHWFor(name="test").to_dict()])

    def tearDown(self) -> None:
        self.p.terminate()
        self.p.join()
        clear_auth_params()
        clear_test_keys()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()  # pragma: no cover
