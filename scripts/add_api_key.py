from sqlalchemy.engine import Engine
import logging

from fleet_management_api.api_impl.api_keys import create_key as _create_key
import fleet_management_api.database.connection as _connection
import fleet_management_api.script_args as _args


logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)


def _add_key_if_key_name_not_already_in_db(connection_source: Engine, api_key_name: str) -> int:
    """Try to add a new API key to the database. If successfull, print the new API key, otherwise print
    message about already existing key name."""
    code, msg = _create_key(key_name=api_key_name, connection_source=connection_source)
    print(msg)
    if code == 200:
        return 0
    else:
        return 1


if __name__ == "__main__":
    args = _args.request_and_get_script_arguments(
        "Add a new API key to the database and if successful, print his or hers API key.",
        _args.PositionalArgInfo("<api-key-name>", str, "The name of the new api key."),
    )

    arguments = args.argvals
    config = args.config

    if config.database.test.strip() != "":
        source = _connection.get_connection_source_test(db_file_path=config.database.test)
    else:  # pragma: no cover
        source = _connection.get_connection_source(
            db_location=config.database.connection.location,
            db_name=config.database.connection.database_name,
            username=config.database.connection.username,
            password=config.database.connection.password,
        )
    code = _add_key_if_key_name_not_already_in_db(source, arguments["<api-key-name>"])
    exit(code)
