import os
from typing import Optional

import sqlalchemy as _sqa
from sqlalchemy import Engine as _Engine
from sqlalchemy import create_engine as _create_engine

from fleet_management_api.database.db_models import (
    Base as _Base,
    CarStateDB as _CarStateDB,
    CarActionStateDB as _CarActionStateDB,
    OrderStateDB as _OrderStateDB,
)
from fleet_management_api.script_args.configs import Database as _Database
from fleet_management_api.api_impl.api_logging import log_info as _log_info, log_error as _log_error


_db_connection: Optional[_Engine] = None


def current_connection_source() -> _Engine | None:
    """Return the current connection source (sqlalchemy Engine object) stored in the module variable."""
    global _db_connection
    return _db_connection


def get_current_connection_source(
    conn_source: Optional[_Engine] = None,
) -> _sqa.engine.base.Engine:
    """Return the passed `conn_source` if it is not None.

    If it is None, do the following:
    - Return the currently used global connection source (sqlalchemy Engine object) stored in the module
    variable, if it is not None.
    - Raise RuntimeError.
    """
    source: Optional[_Engine] = None
    if conn_source is not None:
        source = conn_source
    else:
        source = current_connection_source()
    if source is None:
        raise RuntimeError("No connection source")
    return source


def db_url(
    username: str = "",
    password: str = "",
    location: str = "",
    port: Optional[int] = None,
    db_name: str = "",
) -> str:
    """Compose and return a url used to connect API to the database."""
    if port is not None:
        location = f"{location}:{port}"
    if username == "" and password == "":
        url = f"postgresql+psycopg://{location}"
    elif username == "" and password != "":
        raise ValueError("Cannot specify password without username.")
    else:
        url = f"postgresql+psycopg://{username}:{password}@{location}"
    if db_name != "":
        url = f"{url}/{db_name}"
    return url


def db_url_test(db_file_location: str = "") -> str:
    """Compose and return a url used to connect API to a sqlite database."""
    if db_file_location == "":
        return "sqlite:///:memory:"
    else:
        return f"sqlite:///{db_file_location}"


def is_connected_to_database() -> bool:
    """Return True if the module variable storing the connection source (sqlalchemy Engine object) is not None."""
    if _db_connection is None:
        return False
    try:
        with _db_connection.connect() as conn:
            conn.scalar(_sqa.select(1))
            return True
    except Exception:
        return False


def set_connection_source(
    db_location: str,
    port: Optional[int] = None,
    db_name: str = "",
    username: str = "",
    password: str = "",
) -> None:  # pragma: no cover
    """Set the module variable storing the connection source (sqlalchemy Engine object)."""
    url = db_url(username, password, db_location, port, db_name)
    _set_connection(url)


def restart_connection_source() -> None:
    if _db_connection is None:
        _log_error("Cannot reset connection source if its not currently set.")
    elif _db_connection.url.drivername == "sqlite":
        _log_info("Using sqlite database stored in memory. No need to reset connection source.")
    else:
        url_obj = _db_connection.url
        host = url_obj.host if url_obj.host is not None else ""
        database = url_obj.database if url_obj.database is not None else ""
        password = url_obj.password if url_obj.password is not None else ""
        username = url_obj.username if url_obj.username is not None else ""
        set_connection_source(host, url_obj.port, database, username, password)


def get_connection_source(
    db_location: str,
    port: Optional[int] = None,
    db_name: str = "",
    username: str = "",
    password: str = "",
) -> _Engine:  # pragma: no cover
    """Return a new connection source (sqlalchemy Engine object) (distinct from the one stored in the module variable)."""
    url = db_url(username, password, db_location, port, db_name)
    return _get_connection(url)


def replace_connection_source(source: Optional[_Engine]) -> None:
    """Replace the module variable storing the connection source (sqlalchemy Engine object)."""
    global _db_connection
    _db_connection = source


def get_connection_source_test(db_file_path: str = "", echo: bool = False) -> _Engine:
    """Return a new connection source (sqlalchemy Engine object) (distinct from the one stored in the module variable)."""
    url = db_url_test(db_file_path)
    return _get_connection(url, echo=echo)


def set_connection_source_test(db_file_path: str = "", echo: bool = False) -> str:
    """Set the module variable storing the connection source (sqlalchemy Engine object) to a sqlite database."""
    url = db_url_test(db_file_path)
    if os.path.isfile(db_file_path):
        os.remove(db_file_path)
    _set_connection(url, echo=echo)
    _log_info(f"Using sqlite database stored in file '{db_file_path}'.")
    return db_file_path


def set_up_database(config: _Database) -> None:
    """Set up the database connection source (sqlalchemy Engine object) based on the given configuration.

    Set class attributes of the DB models.
    """
    conn_config = config.connection
    if config.test.strip() != "":
        set_connection_source_test(config.test)
    else:
        set_connection_source(
            db_location=conn_config.location,
            port=conn_config.port,
            db_name=conn_config.database_name,
            username=conn_config.username,
            password=conn_config.password,
        )
    if _db_connection is None:
        raise RuntimeError("Database connection not set up.")
    _CarStateDB.set_max_n_of_stored_states(config.maximum_number_of_table_rows["car_states"])
    _OrderStateDB.set_max_n_of_stored_states(config.maximum_number_of_table_rows["order_states"])
    _CarActionStateDB.set_max_n_of_stored_states(
        config.maximum_number_of_table_rows["car_action_states"]
    )
    src = current_connection_source()
    if src is None:
        msg = "Database connection not set up."
        _log_error(msg)
        raise RuntimeError(msg)
    else:
        msg = f"\nConnected to PostgreSQL database (database url = '{src.url}').\n"
        print(msg)
        _log_info(msg)


def unset_connection_source() -> None:
    """Set the module variable storing the connection source (sqlalchemy Engine object) to None."""
    global _db_connection
    _db_connection = None


def _set_connection(url: str, echo: bool = False) -> None:
    global _db_connection
    _db_connection = _new_connection(url, echo=echo)
    _Base.metadata.create_all(_db_connection)


def _get_connection(url: str, echo: bool = False) -> _Engine:
    global _db_connection
    connection_src = _new_connection(url, echo)
    _Base.metadata.create_all(connection_src)
    return connection_src


def _new_connection(url: str, echo: bool = False) -> _Engine:
    try:
        engine = _create_engine(url, pool_size=100, echo=echo)
        if engine is None:
            raise InvalidConnectionArguments(
                f"Could not create new connection source (url='{url}')."
            )
    except Exception as e:
        raise InvalidConnectionArguments(
            f"Could not create new connection source (url='{url}'). {e}"
        )

    _test_new_connection(engine)
    return engine


def _test_new_connection(engine: _Engine) -> None:
    try:
        engine.connect()
    except Exception as e:
        raise CannotConnectToDatabase(
            "Could not connect to the database with the given connection parameters: \n"
            f"{engine.url}\n\n"
            "Check the location, port number, username and password.\n"
            f"{e}"
        )


class CannotConnectToDatabase(Exception):
    pass


class InvalidConnectionArguments(Exception):
    pass
