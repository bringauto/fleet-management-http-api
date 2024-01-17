#!/usr/bin/env python3

import fleet_management_api.app as app
from fleet_management_api.impl.controllers import init_security
from fleet_management_api.controllers.security_controller import set_public_key
from fleet_management_api.database.connection import set_connection_source, current_connection_source, Base


def main():
    set_connection_source("fleet_management.db")
    Base.metadata.create_all(bind=current_connection_source())
    application = app.get_app()
    application.run(port=8080)


if __name__ == '__main__':
    init_security(
        # keycloak_url=config["security"]["keycloak_url"],
        # client_id=config["security"]["client_id"],
        # secret_key=config["security"]["client_secret_key"],
        # scope=config["security"]["scope"],
        # realm=config["security"]["realm"],
        # callback=config["http_server"]["base_uri"]
        keycloak_url="http://localhost:8081",
        client_id="test_client",
        secret_key="B6BZhMP3CrmffpyI7vdV5DVRkw6klxEe",
        scope="email",
        realm="master",
        callback="http://localhost:8080/v1"
    )
    # public_key_file = open(config["security"]["keycloak_public_key_file"], "r")
    # set_public_key(public_key_file.read())
    # public_key_file.close()
    set_public_key("-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmmAT0cBGSWCeH5QooDRxzS/5zfHZBr2UwH73KnMBF7KbBXbK3qMkSyRz/H5ZhRm2XctWQw55cOXIrTFeiQvZ22Fkot0HnjR4zHdYpPCgwhQTyO6Ig0wbWA6jaooEL/hf2MzNBBZ1NxYvFLZTdjOfYjgTmcs9MBZ/sKboAocKXV/3UY18/ZFvqBpLgs8nFBcok8auiccww6DpX6qqGaHtlEvSf7jqThD0z3BHXi5ZJoj53ToxuMiqPZ22fUlNi5Nu8JW9x9WZjuvcV4sW2c5weQ5oh/PzUzwjJKNWA6TY0wXWaBx7EDvTrXR8FIAWX5L3BZvnC1+ZCk7SrEvId39R9QIDAQAB\n-----END PUBLIC KEY-----")
    main()
