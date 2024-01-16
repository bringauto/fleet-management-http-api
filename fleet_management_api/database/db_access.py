from typing import Any, Dict, Optional, List, Type

from sqlalchemy import insert, select, update
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


def update_record(base: Type[Base], id_name: str, id_value: Any, updated_base) -> ConnexionResponse:
    table = base.__table__
    base_dict = {col:updated_base.__dict__[col] for col in table.columns.keys()}
    with current_connection_source().begin() as conn:
        id_match = getattr(table.columns,id_name) == id_value
        stmt = update(table).where(id_match).values(base_dict)
        try:
            conn.execute(stmt)
            return ConnexionResponse(status_code=200, content_type="string", body="Succesfully updated record")
        except sqaexc.IntegrityError as e:
            return ConnexionResponse(status_code=400, content_type="string", body=str(e.orig))