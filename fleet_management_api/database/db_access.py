from typing import Any, Dict, Optional, List, Type, Literal, Callable
import functools as _functools

import sqlalchemy as _sqa
import sqlalchemy.exc as _sqaexc
from sqlalchemy.orm.exc import NoResultFound as _NoResultFound
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import noload as _noload
from sqlalchemy.orm import InstrumentedAttribute as _InstrumentedAttribute
from connexion.lifecycle import ConnexionResponse as _Response # type: ignore

from fleet_management_api.database.db_models import Base as _Base
from fleet_management_api.database.connection import check_and_return_current_connection_source
import fleet_management_api.database.wait as wait


_ID_NAME = "id"


_wait_mg: wait.WaitObjManager = wait.WaitObjManager()


class ParentNotFound(Exception):
    pass


def add(
    base: Type[_Base],
    *sent_objs: _Base,
    check_reference_existence: Optional[Dict[Type[_Base], int]] = None,
    conn_source: Optional[_sqa.Engine] = None
    ) -> _Response:
    """Adds a objects to the database.

    All the `sent_objs` must be instances of the `base`.

    `check_reference_existence` can be used to check that given ID are present in other tables
    correspoding to the key values in the `check_reference_existence` dictionary.

    The `conn_source` specifies the Sqlalchemy Engine to access the database. If None,
    the globally defined Engine is used.
    """

    global _wait_mg
    if not sent_objs:
        return _Response(status_code=200, content_type="text/plain", body="Nothing to add to database")
    _check_obj_bases_matches_specifed_base(base, *sent_objs)
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session:
        try:
            if check_reference_existence is not None:
                for ref_type, ref_id in check_reference_existence.items():
                    session.get_one(ref_type, ref_id)
            session.add_all([obj.copy() for obj in sent_objs])
            session.commit()
            _wait_mg.notify(base.__tablename__, sent_objs)
            return _Response(status_code=200, content_type="text/plain", body=f"Succesfully sent to database (number of sent objects: {len(sent_objs)}).")
        except _NoResultFound as e:
            return _Response(status_code=404, content_type="text/plain", body=f"{_model_name(base)} with id={ref_id} does not exist in the database.")
        except _sqaexc.IntegrityError as e:
            if "unique" in str(e.orig).lower():
                return _Response(status_code=400, content_type="text/plain", body=f"{_model_name(base)} with id={sent_objs[0].id} already exists in the database.") # type: ignore
            else:
                return _Response(status_code=400, content_type="text/plain", body=f"Nothing added to the database. {e.orig}")
        except Exception as e:
            return _Response(status_code=500, content_type="text/plain", body=f"Error: {e}")


def delete(base: Type[_Base], id_: Any) -> _Response:
    """Delete a single object with ID=`id_` from the database table correspoding to the `base`."""
    source = check_and_return_current_connection_source()
    with _Session(source) as session, session.begin():
        try:
            inst = session.get_one(base, id_)
            session.delete(inst)
            session.commit()
            return _Response(body=f"{_model_name(base)} with {_ID_NAME}={id_} was deleted.", status_code=200)
        except _NoResultFound as e:
            return _Response(status_code=404, content_type="text/plain", body=f"{_model_name(base)} with {_ID_NAME}={id_} not found in table {base.__tablename__}. {e}")
        except _sqaexc.IntegrityError as e:
            return _Response(status_code=400, content_type="text/plain", body=f"{_model_name(base)} with {_ID_NAME}={id_} could not be deleted from table. {e.orig}")
        except Exception as e:
            return _Response(status_code=500, content_type="text/plain", body=f"Error: {e}")


def delete_n(
    base: Type[_Base],
    n: int,
    column_name: str,
    start_from: Literal["minimum", "maximum"],
    criteria: Optional[Dict[str, Callable[[Any],bool]]] = None
    ) -> _Response:
    """Delete multiple instances of the `base`.

    The `base` instances are first filtered by the `criteria` and sorted by values in a column with the `column_name`.
    `n` objects with either `maximum` or `minimum` (defined by the `start_from`) value in the column are deleted.
    """

    if not column_name in base.__table__.columns.keys():
        return _Response(body=f"Column {column_name} not found in table {base.__tablename__}.", status_code=500)
    if criteria is None:
        criteria = {}
    table = base.__table__
    source = check_and_return_current_connection_source()
    with _Session(source) as session, session.begin():
        clauses = [criteria[attr_label](getattr(table.columns, attr_label)) for attr_label in criteria.keys()]
        query = _sqa.select(table.c.id).where(*clauses)
        if start_from == "minimum":
            query = query.order_by(table.c.id)
        else:
            query = query.order_by(table.c.id.desc())
        query = query.limit(n)
        stmt = _sqa.delete(base).where(table.c.id.in_(query))
        n_of_deleted_items = session.execute(stmt).rowcount
        return _Response(
            content_type="text/plain", body=f"{n_of_deleted_items} objects deleted from the database.", status_code=200
        )


def get_by_id(base: Type[_Base], *ids: int, conn_source: Optional[_sqa.Engine] = None) -> List[_Base]:
    """ Returns instances of the `base` with ids from the `ids` tuple.

    The `conn_source` specifies the Sqlalchemy Engine to access the database. If None,
    the globally defined Engine is used.
    """
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session, session.begin():
        try:
            results = []
            for id_value in ids:
                result = session.get(base, id_value)
                if result is not None:
                    results.append(result.copy())
            return results
        except _NoResultFound as e:
            raise _NoResultFound(f"{_model_name(base)} with id={id_value} not found. {e}")
        except Exception as e:
            raise e


def get(
    base: Type[_Base],
    criteria: Optional[Dict[str, Callable[[Any],bool]]] = None,
    wait: bool = False,
    timeout_ms: Optional[int] = None,
    omitted_relationships: Optional[List[_InstrumentedAttribute]] = None,
    conn_source: Optional[_sqa.Engine] = None
    ) -> List[Any]:

    """Get instances of the `base`.

    The objects can be filtered by the `criteria`.

    If `wait`=True and no instances were retrieved from the database after filtering by criteria, the program waits
    until some data that would satisfy the criteria are sent to the database.

    `timeout_ms` is the timeout for the waiting for data in milliseconds.

    `omitted_relationships` contain list of the instance relationship to instances of other bases, that should not be loaded.

    The `conn_source` specifies the Sqlalchemy Engine to access the database. If None,
    the globally defined Engine is used.
    """

    global _wait_mg
    if criteria is None:
        criteria = {}
    table = base.__table__
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session, session.begin():
        clauses = [criteria[attr_label](getattr(table.columns,attr_label)) for attr_label in criteria.keys()]
        stmt = _sqa.select(base).where(*clauses)
        if omitted_relationships is not None:
            for item in omitted_relationships:
                stmt = stmt.options(_noload(item))
        result = [item.copy() for item in session.scalars(stmt).all()]
        if not result and wait:
            result = _wait_mg.wait_and_get_response(
                base.__tablename__,
                timeout_ms,
                validation = _functools.partial(_result_is_ok, criteria)
            )
        return result


def get_children(
    parent_base:Type[_Base],
    parent_id: int,
    children_col_name: str,
    conn_source: Optional[_sqa.Engine] = None
    ) -> List[_Base]:
    """Get children of an instance of `parent_base` with `parent_id` from its `children_col_name`."""

    global _wait_mg
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session:
        try:
            parent = session.get_one(parent_base, parent_id)
            children = list(getattr(parent, children_col_name))
            return children
        except _NoResultFound as e:
            raise ParentNotFound(f"Parent with id={parent_id} not found in table {parent_base.__tablename__}. {e}")
        except Exception as e:
            raise e


def update(updated_obj: _Base) -> _Response:
    """Updates an existing record in the database with the same ID as the updated_obj."""
    table = updated_obj.__table__
    dict_data = _obj_to_dict(updated_obj)
    source = check_and_return_current_connection_source()
    with source.begin() as conn:
        id = updated_obj.__dict__[_ID_NAME]
        id_match = getattr(table.columns, _ID_NAME) == id
        stmt = _sqa.update(table).where(id_match).values(dict_data)
        try:
            result = conn.execute(stmt)
            n_of_updated_items = result.rowcount
            if n_of_updated_items == 0:
                code = 404
                msg = f"Object with {_ID_NAME}={id} was not found in table {updated_obj.__tablename__} in the database. " \
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


def _model_name(base: Type[_Base]) -> str:
    return base.__name__.rstrip("DBModel")


def _result_is_ok(attribute_criteria: Dict[str, Callable[[Any], bool]], item: Any) -> bool:
    for attr_label, attr_criterion in attribute_criteria.items():
        if not hasattr(item, attr_label):
            return False
        if not attr_criterion(item.__dict__[attr_label]):
            return False
    return True