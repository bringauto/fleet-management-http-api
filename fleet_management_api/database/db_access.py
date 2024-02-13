import dataclasses
from typing import Any, Dict, Optional, List, Type, Literal, Callable
import functools as _functools

import sqlalchemy as _sqa
import sqlalchemy.exc as _sqaexc
from sqlalchemy.orm.exc import NoResultFound as _NoResultFound
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import noload as _noload
from sqlalchemy.orm import InstrumentedAttribute as _InstrumentedAttribute
from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

from fleet_management_api.database.db_models import Base as _Base
from fleet_management_api.database.connection import (
    check_and_return_current_connection_source,
)
import fleet_management_api.database.wait as wait


_ID_NAME = "id"


_wait_mg: wait.WaitObjManager = wait.WaitObjManager()


class ParentNotFound(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class _AttributeCondition:
    atribute_name: str
    func: Callable[[Any], bool]
    fail_message: str

    def check(self, obj: _Base) -> None:
        value = getattr(obj, self.atribute_name)
        if not self.func(value):
            raise ValueError(self.fail_message)


class _CheckBeforeAdd:
    def __init__(
        self,
        object_base: Type[_Base],
        id_: int,
        *conditions: _AttributeCondition,
        nullable: bool = False,
    ):
        self._base = object_base
        self._id = id_
        self._conditions = conditions
        self._nullable = nullable

    def check(self, session: _Session) -> None:
        if self._conditions is None:
            self._conditions = {}
        try:
            if self._nullable and self._id is None:
                return
            result = session.get_one(self._base, self._id)
            for condition in self._conditions:
                condition.check(result)

        except _NoResultFound as e:
            raise _NoResultFound(f"{_model_name(self._base)} with ID={self._id} not found. {e}")
        except Exception as e:
            raise e


def add(
    *sent_objs: _Base,
    check_objs: Optional[List[_CheckBeforeAdd]] = None,
    conn_source: Optional[_sqa.Engine] = None,
) -> _Response:
    """Adds a objects to the database.

    All the `sent_objs` must be instances of the same base.

    `check_reference_existence` can be used to check that given ID are present in other tables
    correspoding to the key values in the `check_reference_existence` dictionary.

    The `conn_source` specifies the Sqlalchemy Engine to access the database. If None,
    the globally defined Engine is used.
    """

    global _wait_mg
    if not sent_objs:
        return _Response(
            status_code=200,
            content_type="text/plain",
            body="Nothing to add to database",
        )
    _check_common_base_for_all_objs(*sent_objs)
    _set_all_obj_ids_to_none(*sent_objs)
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session:
        try:
            if check_objs is not None:
                for check_obj in check_objs:
                    try:
                        check_obj.check(session)
                    except _NoResultFound as e:
                        return _Response(
                            status_code=404,
                            content_type="text/plain",
                            body=f"{_model_name(check_obj._base)} with ID={check_obj._id} does not exist in the database.",
                        )
                    except Exception as e:
                        return _Response(
                            status_code=400,
                            content_type="text/plain",
                            body=str(e),
                        )

            session.add_all(sent_objs)
            session.commit()
            inserted_objs = [obj.copy() for obj in sent_objs]
            _wait_mg.notify(sent_objs[0].__tablename__, inserted_objs)
            return _Response(
                status_code=200, content_type="application/json", body=inserted_objs[0]
            )
        except _sqaexc.IntegrityError as e:
            return _Response(
                status_code=400,
                content_type="text/plain",
                body=f"Nothing added to the database. {e.orig}",
            )
        except Exception as e:
            return _Response(
                status_code=500,
                content_type="text/plain",
                body=f"Nothing added to the database. {e}",
            )


def delete(base: Type[_Base], id_: Any) -> _Response:
    """Delete a single object with ID=`id_` from the database table correspoding to the `base`."""
    source = check_and_return_current_connection_source()
    with _Session(source) as session, session.begin():
        try:
            inst = session.get_one(base, id_)
            session.delete(inst)
            session.commit()
            return _Response(
                body=f"{_model_name(base)} with {_ID_NAME}={id_} was deleted.",
                status_code=200,
            )
        except _NoResultFound as e:
            return _Response(
                status_code=404,
                content_type="text/plain",
                body=f"{_model_name(base)} with {_ID_NAME}={id_} not found in table {base.__tablename__}. {e}",
            )
        except _sqaexc.IntegrityError as e:
            return _Response(
                status_code=400,
                content_type="text/plain",
                body=f"{_model_name(base)} with {_ID_NAME}={id_} could not be deleted from table. {e.orig}",
            )
        except Exception as e:
            return _Response(status_code=500, content_type="text/plain", body=f"Error: {e}")


def delete_n(
    base: Type[_Base],
    n: int,
    column_name: str,
    start_from: Literal["minimum", "maximum"],
    criteria: Optional[Dict[str, Callable[[Any], bool]]] = None,
) -> _Response:
    """Delete multiple instances of the `base`.

    The `base` instances are first filtered by the `criteria` and sorted by values in a column with the `column_name`.
    `n` objects with either `maximum` or `minimum` (defined by the `start_from`) value in the column are deleted.
    """

    if not column_name in base.__table__.columns.keys():
        return _Response(
            body=f"Column {column_name} not found in table {base.__tablename__}.",
            status_code=500,
        )
    if criteria is None:
        criteria = {}
    table = base.__table__
    source = check_and_return_current_connection_source()
    with _Session(source) as session, session.begin():
        clauses = [
            criteria[attr_label](getattr(table.columns, attr_label))
            for attr_label in criteria.keys()
        ]
        query = _sqa.select(table.c.id).where(*clauses)
        if start_from == "minimum":
            query = query.order_by(table.c.id)
        else:
            query = query.order_by(table.c.id.desc())
        query = query.limit(n)
        stmt = _sqa.delete(base).where(table.c.id.in_(query))
        n_of_deleted_items = session.execute(stmt).rowcount
        return _Response(
            content_type="text/plain",
            body=f"{n_of_deleted_items} objects deleted from the database.",
            status_code=200,
        )


def get_by_id(
    base: Type[_Base], *ids: int, conn_source: Optional[_sqa.Engine] = None
) -> List[_Base]:
    """Returns instances of the `base` with IDs from the `IDs` tuple.

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
            raise _NoResultFound(f"{_model_name(base)} with ID={id_value} not found. {e}")
        except Exception as e:
            raise e


def get(
    base: Type[_Base],
    criteria: Optional[Dict[str, Callable[[Any], bool]]] = None,
    wait: bool = False,
    timeout_ms: Optional[int] = None,
    omitted_relationships: Optional[List[_InstrumentedAttribute]] = None,
    conn_source: Optional[_sqa.Engine] = None,
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
        clauses = [
            criteria[attr_label](getattr(table.columns, attr_label))
            for attr_label in criteria.keys()
        ]
        stmt = _sqa.select(base).where(*clauses)
        if omitted_relationships is not None:
            for item in omitted_relationships:
                stmt = stmt.options(_noload(item))
        result = [item.copy() for item in session.scalars(stmt).all()]
        if not result and wait:
            result = _wait_mg.wait_and_get_response(
                base.__tablename__,
                timeout_ms,
                validation=_functools.partial(_result_is_ok, criteria),
            )
        return result


def get_children(
    parent_base: Type[_Base],
    parent_id: int,
    children_col_name: str,
    conn_source: Optional[_sqa.Engine] = None,
) -> List[_Base]:
    """Get children of an instance of `parent_base` with `parent_id` from its `children_col_name`."""
    source = _get_checked_connection_source(conn_source)
    with _Session(source) as session:
        try:
            children = list(getattr(session.get_one(parent_base, parent_id), children_col_name))
            return children
        except _NoResultFound as e:
            raise ParentNotFound(
                f"Parent with ID={parent_id} not found in table {parent_base.__tablename__}. {e}"
            )
        except Exception as e:
            raise e


def update(updated_obj: _Base) -> _Response:
    """Updates an existing record in the database with the same ID as the updated_obj."""
    source = check_and_return_current_connection_source()
    with _Session(source) as session, session.begin():
        try:
            session.get_one(updated_obj.__class__, updated_obj.id)
            session.merge(updated_obj)
            code, msg = 200, "Succesfully updated record"
        except _sqaexc.IntegrityError as e:
            code, msg = 400, str(e.orig)
        except _sqaexc.NoResultFound as e:
            code, msg = (
                404,
                f"{_model_name(updated_obj.__class__)} with ID={updated_obj.id} was not found. Nothing to update.",
            )
        except Exception as e:
            code, msg = 500, str(e)
    return _Response(status_code=code, content_type="text/plain", body=msg)


def wait_for_new(
    base: Type[_Base],
    criteria: Optional[Dict[str, Callable[[Any], bool]]] = None,
    timeout_ms: Optional[int] = None,
) -> List[Any]:

    global _wait_mg
    if criteria is None:
        criteria = {}
    result = _wait_mg.wait_and_get_response(
        key=base.__tablename__,
        timeout_ms=timeout_ms,
        validation=_functools.partial(_result_is_ok, criteria),
    )
    return result


def check_obj(
    base: Type[_Base], id_: int, *conditions: _AttributeCondition, nullable: bool = False
) -> _CheckBeforeAdd:
    return _CheckBeforeAdd(base, id_, *conditions, nullable=nullable)


def condition(
    attribute_name: str, func: Callable[[Any], bool], fail_message: str
) -> _AttributeCondition:
    return _AttributeCondition(attribute_name, func, fail_message)


def content_timeout() -> int:
    global _wait_mg
    return _wait_mg.timeout_ms


def set_content_timeout_ms(timeout_ms: int) -> None:
    """Sets the timeout for waiting for content from the database in milliseconds.
    Sets common value for all endpoints with wait mechanism being applied."
    """
    global _wait_mg
    _wait_mg.set_timeout(timeout_ms)


def _check_common_base_for_all_objs(*objs: _Base) -> None:
    if not objs:
        return
    tablename = objs[0].__tablename__
    for obj in objs[1:]:
        if not obj.__tablename__ == tablename:
            raise TypeError(f"Object being added to database must belong to the same table.")


def _get_checked_connection_source(
    source: Optional[_sqa.Engine] = None,
) -> _sqa.engine.base.Engine:
    if source is None:
        return check_and_return_current_connection_source()
    else:
        return check_and_return_current_connection_source(source)


def _model_name(base: Type[_Base]) -> str:
    return base.__name__.replace("DBModel", "")


def _result_is_ok(attribute_criteria: Dict[str, Callable[[Any], bool]], item: Any) -> bool:
    for attr_label, attr_criterion in attribute_criteria.items():
        if not hasattr(item, attr_label):
            return False
        if not attr_criterion(item.__dict__[attr_label]):
            return False
    return True


def _set_all_obj_ids_to_none(*sent_objs: _Base) -> None:
    for obj in sent_objs:
        obj.id = None  # type: ignore
