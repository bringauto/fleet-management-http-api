from typing import Dict, Any
import os

from sqlalchemy import Engine as _Engine
from sqlalchemy import create_engine as _create_engine
import fleet_management_api.database.db_models as _db_models


_db_connection: None|_Engine = None


def current_connection_source() -> _Engine|None:
    global _db_connection
    return _db_connection


def db_url(location: str, db_name: str = "", username: str = "", password: str = "") -> str:
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
    if db_file_location == "":
        return f"sqlite:///:memory:"
    else:
        return f"sqlite:///{db_file_location}"


def set_connection_source(db_location: str, db_name: str = "", username: str = "", password: str = "") -> None: # pragma: no cover
    url = db_url(db_location, db_name, username, password)
    _set_connection(url)


def get_connection_source(db_location: str, db_name: str = "", username: str = "", password: str = "") -> _Engine:
    url = db_url(db_location, db_name, username, password)
    return _get_connection(url)


def get_connection_source_test(db_file_path: str = "") -> _Engine:
    url = db_url_test(db_file_path)
    return _get_connection(url)


def set_connection_source_test(db_file_path: str = "") -> str:
    url = db_url_test(db_file_path)
    if os.path.isfile(db_file_path):
        os.remove(db_file_path)
    _set_connection(url)
    return db_file_path


def set_up_database(config: Dict[str, Any]) -> None:
    conn_config = config["connection"]
    set_connection_source(conn_config["location"], conn_config["database_name"], conn_config["username"], conn_config["password"])
    if _db_connection is None:
        raise RuntimeError("Database connection not set up.")
    _db_models.Base.metadata.create_all(_db_connection)
    _db_models.CarStateDBModel.set_max_n_of_stored_states(config["maximum_number_of_table_rows"]["car_states"])
    _db_models.CarStateDBModel.set_max_n_of_stored_states(config["maximum_number_of_table_rows"]["order_states"])


def unset_connection_source() -> None:
    global _db_connection
    _db_connection = None


def _set_connection(url: str) -> None:
    global _db_connection
    _db_connection = _create_engine(url)
    _db_models.Base.metadata.create_all(_db_connection)


def _get_connection(url: str) -> _Engine:
    global _db_connection
    connection_src = _create_engine(url)
    _db_models.Base.metadata.create_all(connection_src)
    return connection_src