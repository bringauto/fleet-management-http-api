import requests  # type: ignore

import fleet_management_api.script_args as _args
import fleet_management_api.app as app
from fleet_management_api.api_impl.auth_controller import init_security
from fleet_management_api.controllers.security_controller import set_auth_params
from fleet_management_api.database.db_access import set_content_timeout_ms
from fleet_management_api.database.connection import set_up_database
from fleet_management_api.api_impl.data_setup import set_up_data
from fleet_management_api.logs import configure_logging


def _retrieve_keycloak_public_key(keycloak_url: str, realm: str) -> str:
    """Retrieve the public key from the Keycloak server."""
    try:
        response = requests.get(keycloak_url + "/realms/" + realm)
        response.raise_for_status()
    except:
        return ""
    return response.json()["public_key"]


def _set_up_oauth(config: _args.Security) -> None:
    init_security(
        keycloak_url=str(config.keycloak_url),
        client_id=config.client_id,
        secret_key=config.client_secret_key,
        scope=config.scope,
        realm=config.realm,
        callback=str(config.callback),
    )
    set_auth_params(
        public_key=_retrieve_keycloak_public_key(
            keycloak_url=str(config.keycloak_url),
            realm=config.realm,
        ),
        client_id=config.client_id,
    )


if __name__ == "__main__":
    configure_logging("config/logging.json")
    application = app.get_app()
    args = _args.request_and_get_script_arguments(
        "Run the Fleet Management v2 HTTP API server."
    )

    db_config = args.config.database
    api_config = args.config.api
    http_server_config = args.config.http_server
    security_config = args.config.security
    security_config.callback = args.config.http_server.base_uri
    data_config = args.config.data

    set_up_database(db_config)
    set_up_data(data_config)
    set_content_timeout_ms(api_config.request_for_data.timeout_in_seconds * 1000)
    _set_up_oauth(security_config)

    application.run(port=http_server_config.port)
