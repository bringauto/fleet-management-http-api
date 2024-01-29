from typing import Dict, Any

import fleet_management_api.script_args.args as _script_args
import fleet_management_api.app as app
from fleet_management_api.api_impl.auth_controller import init_security
from fleet_management_api.controllers.security_controller import set_public_key
from fleet_management_api.database import set_up_database, set_content_timeout_ms


def set_up_oauth(config: Dict[str, Any]) -> None:
    init_security(
        keycloak_url=config["keycloak_url"],
        client_id=config["client_id"],
        secret_key=config["client_secret_key"],
        scope=config["scope"],
        realm=config["realm"],
        callback=config["callback"]
    )
    public_key_file = open(config["keycloak_public_key_file"], "r")
    set_public_key(public_key_file.read())
    public_key_file.close()


if __name__ == '__main__':
    application = app.get_app()
    args = _script_args.request_and_get_script_arguments("Run the Fleet Management v2 HTTP API server.")

    db_config = args.config["database"]
    api_config = args.config["api"]
    sec_config = args.config["security"]
    sec_config["callback"] = args.config["http_server"]["base_uri"]

    set_up_database(db_config)
    set_content_timeout_ms(api_config["request_for_data"]["timeout_in_seconds"]*1000)
    set_up_oauth(sec_config)
    application.run(port=8080)
