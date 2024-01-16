from typing import Any, Dict, Optional, List, Type

from sqlalchemy import insert, select
from sqlalchemy.orm import Session
import sqlalchemy.exc as sqaexc
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.database.db_models import Base
from fleet_management_api.database.connection import current_connection_source


def send_to_database(base: Type[Base], *data_base: Base) -> ConnexionResponse:
    if not data_base:
        return
    table = base.__table__
    with current_connection_source().begin() as conn:
        stmt = insert(table) # type: ignore
        data_list = [obj.__dict__ for obj in data_base]
        try:
            conn.execute(stmt, data_list)
            return ConnexionResponse(status_code=200, content_type="string", body="Succesfully added to database")
        except sqaexc.IntegrityError as e:
            msg = "Cannot send to database. {e.orig}"
            return ConnexionResponse(status_code=400, content_type="string", body=str(e.orig))


def retrieve_from_database(base: Type[Base], equal_to: Optional[Dict[str, Any]] = None) -> List[Base]:
    if equal_to is None:
        equal_to = {}
    table = base.__table__
    with Session(current_connection_source()) as session:
        clauses = [getattr(table.columns,attr_label)==attr_value for attr_label, attr_value in equal_to.items()]
        stmt = select(base).where(*clauses)
        result = session.execute(stmt)
        return [row[0] for row in result]
