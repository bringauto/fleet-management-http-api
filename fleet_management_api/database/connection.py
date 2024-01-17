from typing import Optional
from sqlalchemy import Engine, create_engine

from fleet_management_api.database.db_models import Base


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
    Base.metadata.create_all(_db_connection)


def set_connection_source(db_file_path: Optional[str] = None) -> None:
    set_test_connection_source(db_file_path)




