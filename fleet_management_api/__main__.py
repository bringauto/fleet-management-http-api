#!/usr/bin/env python3
from typing import Dict
import json

import fleet_management_api.script_args as _script_args
import fleet_management_api.app as app
from fleet_management_api.api_impl.auth_controller import init_security
from fleet_management_api.controllers.security_controller import set_public_key
from fleet_management_api.database import set_up_database, set_content_timeout_ms


def main():
    application = app.get_app()
    args = _script_args.request_and_get_script_arguments("Run the Fleet Management v2 HTTP API server.")
    db_config = args.config["database"]
    api_config = args.config["api"]
    set_up_database(db_config)
    set_content_timeout_ms(api_config["request_for_data"]["timeout_in_seconds"]*1000)
    init_security(
        keycloak_url=args.config["security"]["keycloak_url"],
        client_id=args.config["security"]["client_id"],
        secret_key=args.config["security"]["client_secret_key"],
        scope=args.config["security"]["scope"],
        realm=args.config["security"]["realm"],
        callback=args.config["http_server"]["base_uri"]
    )
    public_key_file = open(args.config["security"]["keycloak_public_key_file"], "r")
    set_public_key(public_key_file.read())
    public_key_file.close()
    application.run(port=8080)


if __name__ == '__main__':
    main()
