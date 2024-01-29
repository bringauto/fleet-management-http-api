from sqlalchemy.engine import Engine

from fleet_management_api.api_impl.api_keys import create_key as _create_key
import fleet_management_api.database.connection as _connection
from fleet_management_api.script_args.args import (
    request_and_get_script_arguments,
    PositionalArgInfo,
)


def _add_key_if_admin_name_not_already_in_db(connection_source: Engine, admin_name: str) -> None:
    """Try to add a new admin key to the database. If successfull, print the new API key, otherwise print
    message about already existing admin."""
    msg = _create_key(key_name=admin_name, connection_source=connection_source)
    print(msg)


if __name__=="__main__":
    vals = request_and_get_script_arguments(
        "Add a new admin to the database and if successful, print his or hers API key.",
        PositionalArgInfo("<admin-name>", str, "The name of the new admin.")
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
    _add_key_if_admin_name_not_already_in_db(source, arguments["<admin-name>"])
