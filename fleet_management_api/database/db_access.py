import dataclasses
from typing import Any, Dict, Optional, List, Type, Literal, Callable
import functools as _functools

import sqlalchemy as _sqa
import sqlalchemy.exc as _sqaexc
from sqlalchemy.orm.exc import NoResultFound as _NoResultFound
from sqlalchemy.orm import (
    Session as _Session,
    noload as _noload,
    InstrumentedAttribute as _InstrumentedAttribute
)
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


class DatabaseRecordValueError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class _AttributeCondition:
    """ An instance of this class binds together the following:
    - an attribute name,
    - a function that checks the attribute value meets condition expressed by the function,
    - a message that is raised when the condition is not met.

    The check method either does nothing or raises exception when the condition is not met.
    """
    atribute_name: str
    func: Callable[[Any], bool]
    fail_message: str

    def check(self, obj: _Base) -> None:
        value = getattr(obj, self.atribute_name)
        if not self.func(value):
            raise DatabaseRecordValueError(self.fail_message)


class _CheckBeforeAdd:
    """An instance of this class binds together the following:
    - a class related to a table in database,
    - an ID of an object in the table,
    - a list of conditions that should be met by the object with the given ID,
    - a flag that indicates that object non-existence is allowed (no exception is raised).

    The check method either does nothing or raises exception when some of the conditions is not met.
    """

    def __init__(
        self,
        object_base: Type[_Base],
        id_: int,
        *conditions: _AttributeCondition,
        allow_nonexistence: bool = False,
    ):
        self._base = object_base
        self._id = id_
        self._conditions = conditions
        self._nullable = allow_nonexistence

    def check(self, session: _Session) -> None:
        """Raise exception if the object with the given ID does not exist in the database
        (when allow_nonexistence is False) or if some of the conditions is not met.

        Otherwise, return None.
        """
        if self._conditions is None:
            self._conditions = {}
        try:
            if self._nullable and self._id is None:
                return
            result = session.get_one(self._base, self._id)
            for condition in self._conditions:
                condition.check(result)

        except _NoResultFound as e:
            raise _NoResultFound(f"{self._base.model_name} with ID={self._id} not found. {e}")
        except Exception as e:
            raise e


def add(
    *added: _Base,
    checked: Optional[List[_CheckBeforeAdd]] = None,
    connection_source: Optional[_sqa.Engine] = None,
) -> _Response:
    """Adds a objects to the database.

    All the `added` must be instances of the same ORM mapped class.

    - The optional `checked` may contain additional conditions put on any other objects contained in the
    database (e.g., existence of object in some table).
    - An optional `connection_source` may be specified to replace the otherwise used global connection source
    (an sqlalchemy Engine object).
    """
    global _wait_mg
    if not added:
        return _Response(
            status_code=200,
            content_type="text/plain",
            body="Nothing to add to database",
        )
    _check_common_base_for_all_objs(*added)
    _set_all_obj_ids_to_none(*added)
    source = check_and_return_current_connection_source(connection_source)
    with _Session(source) as session:
        try:
            if checked is not None:
                for check_obj in checked:
                    check_obj.check(session)
            session.add_all(added)
            session.commit()
            inserted_objs = [obj.copy() for obj in added]
            _wait_mg.notify(added[0].__tablename__, inserted_objs)
            return _Response(
                status_code=200, content_type="application/json", body=inserted_objs
            )
        except _NoResultFound as e:
            return _Response(
                status_code=404,
                content_type="text/plain",
                body=f"{added[0].model_name} with ID={check_obj._id} does not exist in the database.",
            )
        except DatabaseRecordValueError as e:
            return _Response(
                status_code=400,
                content_type="text/plain",
                body=f"Nothing added to the database. {e}",
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
    """Delete a single object with `id_` from the database table correspoding to the mapped class `base`."""
    source = check_and_return_current_connection_source()
    with _Session(source) as session, session.begin():
        try:
            inst = session.get_one(base, id_)
            session.delete(inst)
            session.commit()
            return _Response(
                body=f"{base.model_name} with {_ID_NAME}={id_} was deleted.",
                status_code=200,
            )
        except _NoResultFound as e:
            return _Response(
                status_code=404,
                content_type="text/plain",
                body=f"{base.model_name} with {_ID_NAME}={id_} not found in table {base.__tablename__}. {e}",
            )
        except _sqaexc.IntegrityError as e:
            return _Response(
                status_code=400,
                content_type="text/plain",
                body=f"{base.model_name} with {_ID_NAME}={id_} could not be deleted from table. {e.orig}",
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

    - An optional `connection_source` may be specified to replace the otherwise used global connection source
    (an sqlalchemy Engine object).
    """
    source = check_and_return_current_connection_source(conn_source)
    with _Session(source) as session, session.begin():
        try:
            results = []
            for id_value in ids:
                result = session.get(base, id_value)
                if result is not None:
                    results.append(result.copy())
            return results
        except _NoResultFound as e:
            raise _NoResultFound(f"{base.model_name} with ID={id_value} not found. {e}")
        except Exception as e:
            raise e


def get(
    base: Type[_Base],
    criteria: Optional[Dict[str, Callable[[Any], bool]]] = None,
    wait: bool = False,
    timeout_ms: Optional[int] = None,
    omitted_relationships: Optional[List[_InstrumentedAttribute]] = None,
    connection_source: Optional[_sqa.Engine] = None,
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
    source = check_and_return_current_connection_source(connection_source)
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
                validation=_functools.partial(_is_awaited_result_valid, criteria),
            )
        return result


def get_children(
    parent_base: Type[_Base],
    parent_id: int,
    children_col_name: str,
    connection_source: Optional[_sqa.Engine] = None,
) -> List[_Base]:
    """Get children of an instance of an ORM mapped class `parent_base` with `parent_id` from its `children_col_name`.

    - `children_col_name` is the name of the relationship attribute in the parent_base class.

    - An optional `connection_source` may be specified to replace the otherwise used global connection source
    (an sqlalchemy Engine object).
    """
    source = check_and_return_current_connection_source(connection_source)
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
    """Updates an existing record in the database with the same ID as the updated_obj.

    The updated_obj is an instance of the ORM mapped class related to a table in database.
    """
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
                f"{updated_obj.model_name} with ID={updated_obj.id} was not found. Nothing to update.",
            )
        except Exception as e:
            code, msg = 500, str(e)
    return _Response(status_code=code, content_type="text/plain", body=msg)


def wait_for_new(
    base: Type[_Base],
    criteria: Optional[Dict[str, Callable[[Any], bool]]] = None,
    timeout_ms: Optional[int] = None,
) -> List[Any]:
    """Wait for new instances of the ORM mapped class `base` that satisfy the `criteria` to be sent to the database.

    `timeout_ms` is the timeout for the waiting for data in milliseconds.
    """
    global _wait_mg
    if criteria is None:
        criteria = {}
    result = _wait_mg.wait_and_get_response(
        key=base.__tablename__,
        timeout_ms=timeout_ms,
        validation=_functools.partial(_is_awaited_result_valid, criteria),
    )
    return result


def db_object_check(
    base: Type[_Base], id_: int, *conditions: _AttributeCondition, allow_nonexistence: bool = False
) -> _CheckBeforeAdd:
    """Return an instance of object binding together:
    - a ORM mapped class related to a table in database,
    - an ID of an object in the table,
    - a list of conditions that should be met by the object with the given ID,
    - a flag that indicates that object non-existence is allowed (no exception is raised).

    `base` is a class related to a table in database.
    `id_` is an ID of an object in the table.
    `conditions` is a list of conditions that should be met by the object with the given ID.
    `allow_nonexistence` is a flag that indicates that object non-existence is allowed (no exception is raised and
    checking of conditions is skipped).
    """
    return _CheckBeforeAdd(base, id_, *conditions, allow_nonexistence=allow_nonexistence)


def db_obj_condition(
    attribute_name: str, func: Callable[[Any], bool], fail_message: str
) -> _AttributeCondition:
    """Return an instance of object binding together:
    - an attribute name,
    - a function that checks the attribute value meets condition expressed by the function,
    - a message that is raised when the condition is not met.
    """
    return _AttributeCondition(attribute_name, func, fail_message)


def content_timeout() -> int:
    """Returns the currently set timeout for waiting for content from the database in milliseconds."""
    global _wait_mg
    return _wait_mg.timeout_ms


def set_content_timeout_ms(timeout_ms: int) -> None:
    """Sets the timeout for waiting for content from the database in milliseconds.
    Sets common value for all endpoints with wait mechanism being applied."
    """
    global _wait_mg
    _wait_mg.set_timeout(timeout_ms)


def _check_common_base_for_all_objs(*objs: _Base) -> None:
    """Check if all the `objs` are instances of the same ORM mapped class.

    If not, raise TypeError, otherwise do nothing.
    """
    if not objs:
        return
    tablename = objs[0].__tablename__
    for obj in objs[1:]:
        if not obj.__tablename__ == tablename:
            raise TypeError(f"Object being added to database must belong to the same table.")


def _is_awaited_result_valid(result_attr_criteria: Dict[str, Callable[[Any], bool]], item: Any) -> bool:
    """Return True if the `item` meets all the conditions expressed by the `attribute_criteria`"""
    for attr_label, attr_criterion in result_attr_criteria.items():
        if not hasattr(item, attr_label):
            return False
        if not attr_criterion(item.__dict__[attr_label]):
            return False
    return True


def _set_all_obj_ids_to_none(*sent_objs: _Base) -> None:
    for obj in sent_objs:
        obj.id = None  # type: ignore
