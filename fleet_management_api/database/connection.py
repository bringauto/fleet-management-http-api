from sqlalchemy import Engine, create_engine

from fleet_management_api.database.db_models import Base


DATABASE_URL = "sqlite:///:memory:"


_db_connection: None|Engine = None


def current_connection_source() -> Engine:
    global _db_connection
    return _db_connection


def set_test_connection_source() -> None:
    global _db_connection
    _db_connection = create_engine(DATABASE_URL)
    Base.metadata.create_all(_db_connection)




