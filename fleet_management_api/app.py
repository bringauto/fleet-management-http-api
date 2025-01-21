from __future__ import annotations
from typing import Any, Optional

import jwt
from flask.testing import FlaskClient as _FlaskClient  # type: ignore
import connexion  # type: ignore
from .encoder import JSONEncoder

from fleet_management_api.database.db_models import (
    ApiKeyDB as _ApiKeyDB,
    TenantDB as _TenantDB,
)
from fleet_management_api.database.timestamp import timestamp_ms as _timestamp_ms
from fleet_management_api.api_impl.controllers.order import (
    clear_active_orders,
    clear_inactive_orders,
)
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.api_impl.security import set_key as _set_key


TEST_TENANT_NAME = "test-tenant"
TENANT_COOKIE_NAME = "tenant"
TEST_JWT_KEY = "test_key"


def get_token(*tenants: str) -> str:
    tenant_list = ",".join(f'"/customers/{name}"' for name in tenants)
    return jwt.encode(
        {"Payload": '{{"group": [{tenant_list}]}}'.format(tenant_list=tenant_list)},
        TEST_JWT_KEY,
        algorithm="HS256",
    )


def get_app() -> connexion.FlaskApp:
    app = connexion.App(__name__, specification_dir="./openapi/")
    app.app.json_encoder = JSONEncoder
    app.add_api("openapi.yaml", pythonic_params=True)
    return app


class _TestApp:
    def __init__(self, api_key: str = "") -> None:
        self._app = get_app()
        self._flask_app = self._TestFlaskApp(api_key, self._app.app)

    @property
    def app(self) -> _TestFlaskApp:
        return self._flask_app

    class _TestFlaskApp:
        def __init__(self, api_key, flask_app, *args, **kwargs) -> None:
            self._app = flask_app
            self._api_key = api_key
            self._accessible_tenants: list[str] = []

        def test_client(self, tenant: str = TEST_TENANT_NAME) -> _FlaskClient:
            if self._api_key == "":
                return _TestApp._TestClient(self, self._api_key, tenant=tenant)
            else:
                return self._app.test_client(TEST_TENANT_NAME)

        def def_accessible_tenants(self, *tenants: str) -> None:
            db_tenants = [_TenantDB(name=tenant) for tenant in tenants]
            self._accessible_tenants = list(tenants)
            _db_access.add_without_tenant(*db_tenants)

    class _TestClient(_FlaskClient):
        def __init__(self, application, api_key: str, tenant: str, *args, **kwargs) -> None:
            super().__init__(application._app, *args, **kwargs)
            if tenant:
                self.set_cookie("localhost", TENANT_COOKIE_NAME, tenant)
            self._app = application
            self._key = api_key

        def get(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().get(url, *args, **kwargs, headers=self._get_headers())

        def head(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().head(url, *args, **kwargs, headers=self._get_headers())

        def post(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().post(url, *args, **kwargs, headers=self._get_headers())

        def put(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().put(url, *args, **kwargs, headers=self._get_headers())

        def delete(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().delete(url, *args, **kwargs, headers=self._get_headers())

        def _insert_key(self, uri: str) -> str:
            if "?" in uri:
                uri_base, query_params = uri.split("?")
                return uri_base + f"?api_key={self._key}" + "&" + query_params
            else:
                return uri + f"?api_key={self._key}"

        def _get_headers(self) -> dict[str, str]:
            accessible_tenants = self._app._accessible_tenants
            return {"Authorization": f"Bearer {get_token(*accessible_tenants)}"}


def get_test_app(
    predef_api_key: str = "",
    tenants: Optional[list[str]] = None,
    jwt_key: str = TEST_JWT_KEY,
) -> _TestApp:
    """Creates a test app that can be used for testing purposes.

    It enables to surpass the API key verification by providing a predefined API key.

    If the api_key is left empty, no authentication is required.
    The api_key can be set to any value, that can be used as a value for 'api_key' query parameter in the API calls.
    """
    try:
        _db_access.add_without_tenant(
            _ApiKeyDB(key=predef_api_key, name="test_key", creation_timestamp=_timestamp_ms()),
        )
    except:
        print("API key already exists")
    if tenants is None:
        tenants = []

    tenants.append(TEST_TENANT_NAME)
    clear_active_orders()
    clear_inactive_orders()
    _set_key(jwt_key)
    app = _TestApp(predef_api_key)
    app.app.def_accessible_tenants(*tenants)
    return app
