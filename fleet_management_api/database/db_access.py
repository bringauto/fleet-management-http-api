from typing import Any, Dict, Optional, List, Type, Literal, Callable, Set
import functools as _functools

import sqlalchemy as _sqa
import sqlalchemy.exc as _sqaexc
from sqlalchemy.orm import Session as _Session
from connexion.lifecycle import ConnexionResponse as _Response # type: ignore

from fleet_management_api.database.db_models import Base as _Base
from fleet_management_api.database.connection import check_and_return_current_connection_source
import fleet_management_api.database.wait as wait


_DATABASE_RECORD_ID_NAME = "id"


_wait_mg: wait.WaitObjManager = wait.WaitObjManager()


def add(
    base: Type[_Base],
    *sent_objs: _Base,
    conn_source: Optional[_sqa.Engine] = None,
    check_reference_existence: Optional[Dict[Type[_Base], int]] = None
    ) -> _Response:

    global _wait_mg
    if not sent_objs:
        return _Response(status_code=200, content_type="text/plain", body="Nothing to add to database")
    _check_obj_bases_matches_specifed_base(base, *sent_objs)
    source = _get_checked_connection_source(conn_source)
    with source.begin() as conn:
        if check_reference_existence is not None:
            response = _check_referenced_obj_exists(conn, check_reference_existence)
            if response.status_code != 200:
                return response
        table = base.__table__
        stmt = _sqa.insert(table)
        data_list = [obj.__dict__ for obj in sent_objs]
        try:
            result = conn.execute(stmt, data_list)
            _wait_mg.notify(base.__tablename__, sent_objs)
            return _Response(status_code=200, content_type="text/plain", body=f"Succesfully sent to database (number of sent objects: {result.rowcount}).")
        except _sqaexc.IntegrityError as e:
            return _Response(status_code=400, content_type="text/plain", body=f"Nothing added to the database. {e.orig}")
        except Exception as e:
            return _Response(status_code=500, content_type="text/plain", body=f"Error: {e}")


def delete(base_type: Type[_Base], id_name: str, id_value: Any) -> _Response:
    table = base_type.__table__
    source = check_and_return_current_connection_source()
    with _Session(source) as session:
        id_match = getattr(table.columns,id_name) == id_value
        item = session.query(base_type).filter(id_match).first()
        if item is None:
            return _Response(body=f"Object with {id_name}={id_value} was not found in table " \
                                     f"{base_type.__tablename__}. Nothing to delete.", status_code=404
                                    )
        else:
            session.delete(item)
            session.commit()
            return _Response(body=f"Object with {id_name}={id_value} was deleted from table.", status_code=200)


def delete_n(base_type: Type[_Base], n: int, id_name: str, start_from: Literal["minimum", "maximum"]) -> _Response:
    table = base_type.__table__
    if not id_name in table.columns.keys():
        return _Response(body=f"Column {id_name} not found in table {base_type.__tablename__}.", status_code=500)
    source = check_and_return_current_connection_source()
    with source.begin() as conn:
        if start_from == "minimum":
            subquery = _sqa.select(table.c.id).order_by(table.c.id).limit(n).alias()
        else:
            subquery = _sqa.select(table.c.id).order_by(table.c.id.desc()).limit(n).alias()
        stmt = _sqa.delete(table).where(table.c.id.in_(subquery))
        result = conn.execute(stmt)
        n_of_deleted_items = result.rowcount
        if n_of_deleted_items == 0:
            return _Response(content_type="text/plain", body="Nothing deleted from the database.", status_code=200)
        else:
            return _Response(
                content_type="text/plain", body=f"{n_of_deleted_items} objects deleted from the database.", status_code=200
            )


def _result_is_ok(attribute_criteria: Dict[str, Callable[[Any], bool]], item: Any) -> bool:
    for attr_label, attr_criterion in attribute_criteria.items():
        if not hasattr(item, attr_label):
            return False
        if not attr_criterion(item.__dict__[attr_label]):
            return False
    return True


def get(
    base: Type[_Base],
    criteria: Optional[Dict[str, Callable[[Any],bool]]] = None,
    wait: bool = False,
    timeout_ms: Optional[int] = None,
    conn_source: Optional[_sqa.Engine] = None
    ) -> List[Any]:

    global _wait_mg
    if criteria is None:
        criteria = {}
    table = base.__table__
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session:
        clauses = [criteria[attr_label](getattr(table.columns,attr_label)) for attr_label in criteria.keys()]
        stmt = _sqa.select(base).where(*clauses)
        result = [row[0] for row in session.execute(stmt)]
        if not result and wait:
            result = _wait_mg.wait_and_get_response(
                base.__tablename__,
                timeout_ms,
                validation = _functools.partial(_result_is_ok, criteria)
            )
        result = result
        return result


def get_children(
    parent_type:Type[_Base],
    parent_id: int,
    children_col_name: str,
    conn_source: Optional[_sqa.Engine] = None
    ) -> List[_Base]:

    global _wait_mg
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session:
        parent = session.query(parent_type).filter(parent_type.id==parent_id).first() # type: ignore
        if parent is None:
            return []
        children = list(getattr(parent, children_col_name))
        return children


def update(updated_obj: _Base) -> _Response:
    table = updated_obj.__table__
    dict_data = _obj_to_dict(updated_obj)
    source = check_and_return_current_connection_source()
    with source.begin() as conn:
        id = updated_obj.__dict__[_DATABASE_RECORD_ID_NAME]
        id_match = getattr(table.columns, _DATABASE_RECORD_ID_NAME) == id
        stmt = _sqa.update(table).where(id_match).values(dict_data)
        try:
            result = conn.execute(stmt)
            n_of_updated_items = result.rowcount
            if n_of_updated_items == 0:
                code = 404
                msg = f"Object with {_DATABASE_RECORD_ID_NAME}={id} was not found in table {updated_obj.__tablename__} in the database. " \
                    "Nothing to update."
            else:
                code, msg = 200, "Succesfully updated record"
        except _sqaexc.IntegrityError as e:
            code, msg = 400, str(e.orig)
    return _Response(status_code=code, content_type="text/plain", body=msg)


def wait_for_new(
    base: Type[_Base],
    criteria: Optional[Dict[str, Callable[[Any],bool]]] = None,
    timeout_ms: Optional[int] = None
    ) -> List[Any]:

    global _wait_mg
    if criteria is None:
        criteria = {}

    result = _wait_mg.wait_and_get_response(
        key=base.__tablename__,
        timeout_ms=timeout_ms,
        validation=_functools.partial(_result_is_ok, criteria)
    )
    return result


def content_timeout() -> int:
    global _wait_mg
    return _wait_mg.timeout_ms


def set_content_timeout_ms(timeout_ms: int) -> None:
    """Sets the timeout for waiting for content from the database in milliseconds.
    Sets common value for all endpoints with wait mechanism being applied."
    """
    global _wait_mg
    _wait_mg.set_timeout(timeout_ms)


def _check_obj_bases_matches_specifed_base(specified_base: Type[_Base], *objs: _Base) -> None:
    for obj in objs:
        if not isinstance(obj, specified_base):
            raise TypeError(f"Object {obj} is not of type {specified_base}")


def _get_checked_connection_source(source: Optional[_sqa.Engine] = None) -> _sqa.engine.base.Engine:
    if source is None:
        return check_and_return_current_connection_source()
    else:
        return check_and_return_current_connection_source(source)


def _obj_to_dict(obj: _Base) -> Dict[str, Any]:
    return {col:obj.__dict__[col] for col in obj.__table__.columns.keys()}


def _check_referenced_obj_exists(connection: _sqa.Connection, check_reference_existence: Dict[Type[_Base], int]) -> _Response:
    for ref_type, ref_id in check_reference_existence.items():
        stmt = _sqa.select(ref_type).where(ref_type.id == ref_id)
        result = connection.execute(stmt).first()
        if result is None:
            return _Response(status_code=404, content_type="text/plain", body=f"Reference to {ref_type.__name__} with id={ref_id} does not exist in the database.")

    return _Response(status_code=200, content_type="text/plain", body=f"All referenced objects exist in the database.")