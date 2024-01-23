from typing import Dict, Any
from sqlalchemy import Engine, create_engine

import fleet_management_api.database.db_models as db_models


_db_connection: None|Engine = None


def current_connection_source() -> Engine:
    global _db_connection
    return _db_connection


def db_url_production(location: str, username: str = "", password: str = "", db_name: str = "") -> str:
    if username == "" and password == "":
        return f"postgresql:psycopg://{location}/{db_name}"
    elif username == "" and password != "":
        return "Error when connecting to database: Missing username."
    else:
        return f"postgresql:psycopg://{username}:{password}@{location}/{db_name}"


def db_url_test(db_file_location: str = "") -> str:
    if db_file_location == "":
        return f"sqlite:///:memory:"
    else:
        return f"sqlite:///{db_file_location}"


def set_connection_source(db_location: str, db_name: str = "", username: str = "", password: str = "") -> None:
    url = db_url_production(db_location, db_name, username, password)
    _set_connection(url)


def set_test_connection_source(db_file_path: str = "") -> None:
    global _db_connection
    url = db_url_test(db_file_path)
    _db_connection = create_engine(url)
    db_models.Base.metadata.create_all(_db_connection)


def set_up_database(config: Dict[str, Any]) -> None:
    db_models.Base.metadata.create_all(_db_connection)
    db_models.CarStateDBModel.set_max_number_of_stored_states(config["maximum_number_of_table_rows"]["car_states"])
    db_models.CarStateDBModel.set_max_number_of_stored_states(config["maximum_number_of_table_rows"]["order_states"])


def _set_connection(url: str) -> None:
    global _db_connection
    _db_connection = create_engine(url)
    db_models.Base.metadata.create_all(_db_connection)