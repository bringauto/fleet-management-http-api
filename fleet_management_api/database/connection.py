from typing import Optional, Dict, Any
from sqlalchemy import Engine, create_engine

import fleet_management_api.database.db_models as db_models


DEFAULT_DATABASE_URL = "sqlite:///:memory:"


_db_connection: None|Engine = None


def current_connection_source() -> Engine:
    global _db_connection
    return _db_connection


def set_test_connection_source(db_file_path: Optional[str] = None) -> None:
    global _db_connection
    if db_file_path is None:
        db_file_path = DEFAULT_DATABASE_URL
    else:
        db_file_path = f"sqlite:///{db_file_path}"
    _db_connection = create_engine(db_file_path)
    db_models.Base.metadata.create_all(_db_connection)


def set_connection_source(db_file_path: Optional[str] = None) -> None:
    set_test_connection_source(db_file_path)


def set_up_database(config: Dict[str, Any]) -> None:
    db_models.Base.metadata.create_all(_db_connection)
    db_models.CarStateDBModel.set_max_number_of_stored_states(config["maximum_number_of_table_rows"]["car_states"])
    db_models.CarStateDBModel.set_max_number_of_stored_states(config["maximum_number_of_table_rows"]["order_states"])


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
