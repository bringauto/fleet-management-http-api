from sqlalchemy.engine import Engine

from fleet_management_api.api_impl.api_keys import create_key as _create_key
import fleet_management_api.database.connection as _connection
from fleet_management_api.script_args.args import (
    request_and_get_script_arguments,
    PositionalArgInfo,
)


def _add_key_if_key_name_not_already_in_db(connection_source: Engine, api_key_name: str) -> int:
    """Try to add a new API key to the database. If successfull, print the new API key, otherwise print
    message about already existing key name."""
    code, msg = _create_key(key_name=api_key_name, connection_source=connection_source)
    print(msg)
    if code==200:
        return 0
    else:
        return 1


if __name__=="__main__":
    vals = request_and_get_script_arguments(
        "Add a new API key to the database and if successful, print his or hers API key.",
        PositionalArgInfo("<api-key-name>", str, "The name of the new api key.")
    )
    arguments = vals.argvals
    config = vals.config
    if "test" in arguments.keys():
        source = _connection.get_connection_source_test(db_file_path=arguments["test"])
    else: # pragma: no cover
        source = _connection.get_connection_source(
            db_location=(arguments["location"]+":"+str(arguments["port"])),
            db_name=arguments["database_name"],
            username=arguments["username"],
            password=arguments["password"]
        )
    code = _add_key_if_key_name_not_already_in_db(source, arguments["<api-key-name>"])
    exit(code)
