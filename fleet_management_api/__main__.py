import fleet_management_api.script_args as _args
import fleet_management_api.app as app
from fleet_management_api.api_impl.auth_controller import init_security
from fleet_management_api.controllers.security_controller import set_public_key
from fleet_management_api.database import set_up_database, set_content_timeout_ms


def _set_up_oauth(config: _args.Security) -> None:
    init_security(
        keycloak_url=str(config.keycloak_url),
        client_id=config.client_id,
        secret_key=config.client_secret_key,
        scope=config.scope,
        realm=config.realm,
        callback=str(config.callback),
    )
    with open(config.keycloak_public_key_file, "r") as public_key_file:
        set_public_key(public_key_file.read())


if __name__ == "__main__":
    application = app.get_app()
    args = _args.request_and_get_script_arguments(
        "Run the Fleet Management v2 HTTP API server."
    )

    db_config = args.config.database
    api_config = args.config.api
    http_server_config = args.config.http_server
    security_config = args.config.security
    security_config.callback = args.config.http_server.base_uri

    set_up_database(db_config)
    set_content_timeout_ms(api_config.request_for_data.timeout_in_seconds * 1000)
    _set_up_oauth(security_config)

    application.run(port=http_server_config.port)
