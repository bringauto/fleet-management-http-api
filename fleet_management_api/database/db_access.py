from typing import Any, Dict, Optional, List, Type

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from fleet_management_api.database.db_models import Base
from fleet_management_api.database.connection import current_connection_source


def send_to_database(base: Type[Base], *data_base: Base) -> None:
    if not data_base:
        return
    table = base.__table__
    with current_connection_source().begin() as conn:
        stmt = insert(table) # type: ignore
        data_list = [obj.__dict__ for obj in data_base]
        conn.execute(stmt, data_list)


def retrieve_from_database(base: Type[Base], equal_to: Optional[Dict[str, Any]] = None) -> List[Base]:
    if equal_to is None:
        equal_to = {}
    table = base.__table__
    with Session(current_connection_source()) as session:
        if not equal_to:
            stmt = select(base)
        else:
            clauses = [getattr(table.columns, attr_label) == attr_value for attr_label, attr_value in equal_to.items()]
            stmt = select(base).where(*clauses)
        result = session.execute(stmt)
        return [row[0] for row in result]
