from __future__ import annotations
from typing import Any

from flask.testing import FlaskClient as _FlaskClient  # type: ignore
import connexion  # type: ignore

from .encoder import JSONEncoder
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import ApiKeyDBModel as _ApiKeyDBModel
from fleet_management_api.database.timestamp import timestamp_ms as _timestamp_ms
from fleet_management_api.api_impl.controllers.order_state import initialize_last_order_status_dict
from fleet_management_api.api_impl.controllers.order import (
    clear_n_of_active_orders,
    max_n_of_active_orders,
    n_of_active_orders,
    set_max_n_of_active_orders
)


def get_app() -> connexion.FlaskApp:
    initialize_last_order_status_dict()
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

        def test_client(self) -> _FlaskClient:
            if self._api_key == "":
                return _TestApp._TestClient(self._app, self._api_key)
            else:
                return self._app.test_client()

    class _TestClient(_FlaskClient):
        def __init__(self, application, api_key: str, *args, **kwargs) -> None:
            super().__init__(application, *args, **kwargs)
            self._key = api_key

        def get(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().get(url, *args, **kwargs)

        def head(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().head(url, *args, **kwargs)

        def post(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().post(url, *args, **kwargs)

        def put(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().put(url, *args, **kwargs)

        def delete(self, url: str, *args, **kwargs) -> Any:
            url = self._insert_key(url)
            return super().delete(url, *args, **kwargs)

        def _insert_key(self, uri: str) -> str:
            if "?" in uri:
                uri_base, query_params = uri.split("?")
                return uri_base + f"?api_key={self._key}" + "&" + query_params
            else:
                return uri + f"?api_key={self._key}"


def get_test_app(predef_api_key: str = "") -> _TestApp:
    """Creates a test app that can be used for testing purposes.

    It enables to surpass the API key verification by providing a predefined API key.

    If the api_key is left empty, no authentication is required.
    The api_key can be set to any value, that can be used as a value for 'api_key' query parameter in the API calls.
    """
    _db_access.add(
        _ApiKeyDBModel(
            key=predef_api_key, name="test_key", creation_timestamp=_timestamp_ms()
        ),
    )
    return _TestApp(predef_api_key)
