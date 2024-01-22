from typing import Any, Dict, Optional, List, Type, Literal

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session
import sqlalchemy.exc as sqaexc
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.database.db_models import Base
from fleet_management_api.database.connection import current_connection_source


DATABASE_RECORD_ID_NAME = "id"


def add_record(base: Type[Base], *sent_objs: Base) -> ConnexionResponse:
    if not sent_objs:
        return ConnexionResponse(status_code=200, content_type="string", body="Nothing to add to database")
    _check_obj_bases_matches_specifed_base(base, *sent_objs)
    table = base.__table__
    with current_connection_source().begin() as conn:
        stmt = insert(table) # type: ignore
        data_list = [obj.__dict__ for obj in sent_objs]
        try:
            conn.execute(stmt, data_list)
            return ConnexionResponse(status_code=200, content_type="string", body="Succesfully added record to database")
        except sqaexc.IntegrityError as e:
            return ConnexionResponse(status_code=400, content_type="string", body=f"Nothing added to the database. {e.orig}")


def delete_record(base_type: Type[Base], id_name: str, id_value: Any) -> ConnexionResponse:
    table = base_type.__table__
    with current_connection_source().begin() as conn:
        id_match = getattr(table.columns,id_name) == id_value
        stmt = table.delete().where(id_match)
        result = conn.execute(stmt)
        n_of_deleted_items = result.rowcount
        if n_of_deleted_items == 0:
            return ConnexionResponse(body=f"Object with {id_name}={id_value} was not found in table " \
                                     f"{base_type.__tablename__}. Nothing to delete.", status_code=404
                                    )
        else:
            return ConnexionResponse(body=f"Object with {id_name}={id_value} was deleted from table " \
                                     f"{base_type.__tablename__}.", status_code=200
                                    )


def delete_n_records(base_type: Type[Base], n: str, id_name: str, start_from: Literal["minimum", "maximum"]) -> ConnexionResponse:
    table = base_type.__table__
    if not id_name in table.columns.keys():
        return ConnexionResponse(body=f"Column {id_name} not found in table {base_type.__tablename__}.", status_code=500)

    with current_connection_source().begin() as conn:
        if start_from == "minimum":
            subquery = select(table.c.id).order_by(table.c.id).limit(n).alias()
        else:
            subquery = select(table.c.id).order_by(table.c.id.desc()).limit(n).alias()
        stmt = table.delete().where(table.c.id.in_(subquery))
        result = conn.execute(stmt)
        n_of_deleted_items = result.rowcount
        if n_of_deleted_items == 0:
            return ConnexionResponse(content_type="text/plain", body="Nothing deleted from the database.", status_code=200)
        else:
            return ConnexionResponse(
                content_type="text/plain", body=f"{n_of_deleted_items} objects deleted from the database.", status_code=200
            )


def get_records(base: Type[Base], equal_to: Optional[Dict[str, Any]] = None) -> List[Base]:
    if equal_to is None:
        equal_to = {}
    table = base.__table__
    with Session(current_connection_source()) as session:
        clauses = [getattr(table.columns,attr_label)==attr_value for attr_label, attr_value in equal_to.items()]
        stmt = select(base).where(*clauses)
        result = session.execute(stmt)
        return [row[0] for row in result]


def update_record(updated_obj: Base) -> ConnexionResponse:
    table = updated_obj.__table__
    dict_data = _obj_to_dict(updated_obj)
    with current_connection_source().begin() as conn:
        id = updated_obj.__dict__[DATABASE_RECORD_ID_NAME]
        id_match = getattr(table.columns, DATABASE_RECORD_ID_NAME) == id
        stmt = update(table).where(id_match).values(dict_data)
        try:
            result = conn.execute(stmt)
            n_of_updated_items = result.rowcount
            if n_of_updated_items == 0:
                code = 404
                msg = f"Object with {DATABASE_RECORD_ID_NAME}={id} was not found in table {updated_obj.__tablename__} in the database. " \
                    "Nothing to update."
            else:
                code, msg = 200, "Succesfully updated record"
        except sqaexc.IntegrityError as e:
            code, msg = 400, e.orig
    return ConnexionResponse(status_code=code, content_type="string", body=msg)


def _check_obj_bases_matches_specifed_base(specified_base: Type[Base], *objs: Base) -> None:
    for obj in objs:
        if not isinstance(obj, specified_base):
            raise TypeError(f"Object {obj} is not of type {specified_base}")


def _obj_to_dict(obj: Base) -> Dict[str, Any]:
    return {col:obj.__dict__[col] for col in obj.__table__.columns.keys()}