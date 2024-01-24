from typing import Any, Dict, Optional, List, Type, Literal
import functools

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session
import sqlalchemy.exc as sqaexc
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.database.db_models import Base
from fleet_management_api.database.connection import current_connection_source
import fleet_management_api.database.wait as wait


_DATABASE_RECORD_ID_NAME = "id"


_wait_mg: wait.WaitObjManager = wait.WaitObjManager()


def content_timeout() -> int:
    global _wait_mg
    return _wait_mg.timeout()


def set_content_timeout_ms(timeout_ms: int) -> None:
    """Sets the timeout for waiting for content from the database in milliseconds.

    Sets common value for all endpoints with wait mechanism being applied."
    """
    global _wait_mg
    _wait_mg.set_timeout(timeout_ms)


def add_record(base: Type[Base], *sent_objs: Base) -> ConnexionResponse:
    global _wait_mg
    if not sent_objs:
        return ConnexionResponse(status_code=200, content_type="string", body="Nothing to add to database")
    _check_obj_bases_matches_specifed_base(base, *sent_objs)
    table = base.__table__
    with current_connection_source().begin() as conn:
        stmt = insert(table) # type: ignore
        data_list = [obj.__dict__ for obj in sent_objs]
        try:
            result = conn.execute(stmt, data_list)
            if result.rowcount == 0:
                return ConnexionResponse(status_code=200, content_type="string", body="Nothing added to the database")
            else:
                _wait_mg.notify(base.__tablename__, sent_objs)
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


def _result_is_ok(item: Any, equal_to: Dict[str, Any]) -> bool:
    for attr_label, attr_value in equal_to.items():
        if not hasattr(item, attr_label):
            return False
        if item.__dict__[attr_label] != attr_value:
            return False
    return True


def get_records(
    base: Type[Base],
    equal_to: Optional[Dict[str, Any]] = None,
    wait: bool = False,
    timeout_ms: Optional[int] = None
    ) -> List[Base]:

    global _wait_mg
    if equal_to is None:
        equal_to = {}
    table = base.__table__
    with Session(current_connection_source()) as session:
        clauses = [getattr(table.columns,attr_label)==attr_value for attr_label, attr_value in equal_to.items()]
        stmt = select(base).where(*clauses)
        result = [row[0] for row in session.execute(stmt)]
        if not result and wait:
            result = _wait_mg.wait_and_get_response(
                base.__tablename__,
                timeout_ms,
                validation = functools.partial(_result_is_ok, equal_to=equal_to)
            )
        return result


def update_record(updated_obj: Base) -> ConnexionResponse:
    table = updated_obj.__table__
    dict_data = _obj_to_dict(updated_obj)
    with current_connection_source().begin() as conn:
        id = updated_obj.__dict__[_DATABASE_RECORD_ID_NAME]
        id_match = getattr(table.columns, _DATABASE_RECORD_ID_NAME) == id
        stmt = update(table).where(id_match).values(dict_data)
        try:
            result = conn.execute(stmt)
            n_of_updated_items = result.rowcount
            if n_of_updated_items == 0:
                code = 404
                msg = f"Object with {_DATABASE_RECORD_ID_NAME}={id} was not found in table {updated_obj.__tablename__} in the database. " \
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