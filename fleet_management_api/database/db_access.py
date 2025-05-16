import dataclasses
from typing import Any, Optional, Literal, Callable, Iterable, ParamSpec, TypeVar, Protocol
import functools as _functools
import logging as _logging

import sqlalchemy as _sqa
import sqlalchemy.exc as _sqaexc
from sqlalchemy.orm.exc import NoResultFound as _NoResultFound
from sqlalchemy.orm import (
    Session as _Session,
    noload as _noload,
    InstrumentedAttribute as _InstrumentedAttribute,
)
from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

from fleet_management_api.logs import LOGGER_NAME
from fleet_management_api.database.db_models import (
    Base as _Base,
    TenantDB as _TenantDB,
    Tenants as Tenants,
    SessionWithTenants as _SessionWithTenants,
)
from fleet_management_api.database.connection import (
    get_current_connection_source as _get_current_connection_source,
    restart_connection_source as _restart_connection_source,
)
import fleet_management_api.database.wait as wait
from fleet_management_api.api_impl.api_responses import (
    json_response as _json_response,
    text_response as _text_response,
    error as _error,
)
from fleet_management_api.api_impl.tenants import (
    NO_TENANTS as _NO_TENANTS,
    TenantNotAccessible as _TenantNotAccessible,
)


P = ParamSpec("P")
T = TypeVar("T")


logger = _logging.getLogger(LOGGER_NAME)
_wait_mg: wait.WaitObjManager = wait.WaitObjManager()


Order = Literal["asc", "desc"]
ColumnName = str
Criteria = dict[str, Callable[[Any], bool]] | None


class DuplicateError(Exception):
    """Raised when an object already exists in the database."""

    pass


class ParentNotFound(Exception):
    """Raised when the parent object does not exist in the database."""

    pass


class DatabaseRecordValueError(Exception):
    """Raised when the value of the record in the database does not meet the condition."""

    pass


class UnspecifiedTenant(Exception):
    """Raised when the tenant is not specified in the request."""

    pass


class TenantDoesNotExist(Exception):
    """Raised when the tenant does not exist in the database."""

    pass


@dataclasses.dataclass(frozen=True)
class _AttributeCondition:
    """An instance of this class binds together the following:
    - an attribute name,
    - a function that checks the attribute value meets condition expressed by the function,
    - a message that is raised when the condition is not met.

    The check method either does nothing or raises exception when the condition is not met.
    """

    atribute_name: str
    func: Callable[[Any], bool]
    fail_message: str

    def check(self, obj: _Base) -> bool:
        value = getattr(obj, self.atribute_name)
        if not self.func(value):
            raise DatabaseRecordValueError(self.fail_message)
        return True


class CheckBeforeAdd:
    """An instance of this class binds together the following:
    - a class related to a table in database,
    - an ID of an object in the table,
    - a list of conditions that should be met by the object with the given ID,
    - a flag that indicates that object non-existence is allowed (no exception is raised).

    The check method either does nothing or raises exception when some of the conditions is not met.
    """

    def __init__(
        self,
        object_base: type[_Base],
        id_: int,
        *conditions: _AttributeCondition,
        nullable: bool = False,
    ):
        self._base = object_base
        self._id = id_
        self._conditions = conditions
        self._nullable = nullable

    def check(self, session: _Session) -> None:
        """Raise exception if the object with the given ID does not exist in the database
        (and nullable=False) or if some of the conditions is not met.

        """
        if not self._nullable or self._id is not None:
            result = session.get_one(self._base, self._id)
            all(condition.check(result) for condition in self._conditions)


def db_access_method(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator for the function that restarts the database connection source in case of operational error."""

    @_functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            response: _Response = func(*args, **kwargs)
            if hasattr(response, "status_code") and (response.status_code in (503, 500)):
                raise RuntimeError(response.body)
            return response
        except _sqaexc.OperationalError as e:
            _logging.warning(
                f"Restarting connection source due to a likely deletion of database tables. Error: {e}"
            )
        except Exception as e:
            _logging.warning(f"Restarting connection source due to an database error. Error: {e}")
        _restart_connection_source()
        return func(*args, **kwargs)

    return wrapper


def add_tenants(*names: str) -> _Response:
    """Add tenants to the database."""
    tenants = [_TenantDB(name=name) for name in names]
    response = add_without_tenant(*tenants)
    if response.status_code == 400 and 'null value in column "id"' in response.body["detail"]:
        db_tenants = get_tenants(_NO_TENANTS)
        last_id = max([(t.id or 0) for t in db_tenants]) if db_tenants else 0
        for tenant in tenants:
            last_id += 1
            tenant.id = last_id
        response = add_without_tenant(*tenants, auto_id=False)
    if response.status_code != 200:
        raise RuntimeError(f"Error when adding tenants: {response.body}")
    return response


def add_without_tenant(
    *added: _Base,
    checked: Optional[Iterable[CheckBeforeAdd]] = None,
    connection_source: Optional[_sqa.Engine] = None,
    auto_id: bool = True,
) -> _Response:
    """Add a an object to the database without specifying a tenant.

    For more details see documentation for the `add` method.
    """

    return add(
        _NO_TENANTS, *added, checked=checked, connection_source=connection_source, auto_id=auto_id
    )


def delete_without_tenant(base: type[_Base], id_: int) -> _Response:
    """Delete an object with the given ID from the database without specifying a tenant."""
    return delete(_NO_TENANTS, base, id_)


@db_access_method
def add(
    tenants: Tenants,
    *added: _Base,
    checked: Optional[Iterable[CheckBeforeAdd]] = None,
    connection_source: Optional[_sqa.Engine] = None,
    auto_id: bool = True,
) -> _Response:
    """Adds a objects to the database.

    All the `added` must be instances of the same ORM mapped class.

    - The optional `checked` may contain additional conditions put on any other objects contained in the
    database (e.g., existence of object in some table).
    - An optional `connection_source` may be specified to replace the otherwise used global connection source
    (an sqlalchemy Engine object).
    """

    source = _get_current_connection_source(connection_source)
    if not added:
        return _json_response([])
    _check_common_base_for_all_objs(*added)

    if tenants is not _NO_TENANTS and not added[0].state:
        if not tenants.current:
            return _error(401, "Tenant not received in the request.", title="Tenant not received.")

        code = _set_tenant_id_to_all_objs(tenants.current, *added)
        if code != 200:
            msg = f"Tenant '{tenants.current}' does not exist."
            return _error(code, msg, title="Tenant does not exist.")

    global _wait_mg
    with _SessionWithTenants(source, tenants=tenants) as session:
        try:
            if checked is not None:
                result = _check_before_add(session, checked)
                if result.status_code != 200:
                    return result
            if auto_id:
                _set_id_to_none(list(added))
            session.add_all(added)
            session.commit()
            _wait_mg.notify_about_content(added[0].__tablename__, added)
            return _json_response([obj.copy() for obj in added])
        except _TenantNotAccessible as e:
            return _error(401, str(e), title="Tenant not accessible")
        except DatabaseRecordValueError as e:
            return _error(
                400,
                f"Cannot create object. Nothing added to the database. {e}",
                title="Unmet conditions on the added or or referenced object",
            )
        except _sqaexc.IntegrityError as e:
            return _error(
                400,
                f"Cannot create object. Nothing added to the database. {e.orig}",
                title="ID conflict in the database",
            )
        except Exception as e:
            return _error(
                500,
                f"Cannot create object. Nothing added to the database. {e}",
                title="Unexpected error",
            )


@db_access_method
def delete(tenants: Tenants, base: type[_Base], id_: Any) -> _Response:
    """Delete a single object with `id_` from the database table correspoding to the mapped class `base`."""
    source = _get_current_connection_source()
    if base.owned_by_tenant():
        response = _check_and_set_tenant(tenants, base(id=id_))
        if response.status_code != 200:
            return response
    with _Session(source) as session:
        try:
            inst = session.get_one(base, id_)
            session.delete(inst)
            session.commit()
            return _text_response(f"{base.model_name} (ID={id_}) has been deleted.")
        except _NoResultFound as e:
            msg = f"{base.model_name} (ID={id_}) not found. {e}"
            return _error(404, msg, title="Object to delete not found")
        except _sqaexc.IntegrityError as e:
            msg = f"Could not delete {base.model_name} (ID={id_}). {e.orig}"
            return _error(400, msg, title="Cannot delete object due to integrity error")
        except Exception as e:
            return _error(500, f"Error: {e}", "Cannot delete object due to unexpected error.")


@db_access_method
def delete_n(
    base: type[_Base],
    n: int,
    column_name: str,
    start_from: Literal["minimum", "maximum"],
    criteria: Criteria = None,
) -> _Response:
    """Delete multiple instances of the `base`.

    The `base` instances are first filtered by the `criteria` and sorted by values in a column with
    the `column_name`.
    `n` objects with either `maximum` or `minimum` (defined by the `start_from`) value in the column
    are deleted.
    """

    table = base.__table__
    sort_col = table.c.get(column_name, None)
    if sort_col is None:
        msg = f"Column {column_name} not found in table {base.__tablename__}."
        return _error(500, msg, title="Invalid request to the server' database")
    source = _get_current_connection_source()
    with _Session(source) as session, session.begin():
        id_col = table.c["id"]
        order_by = table.c[column_name] if start_from == "minimum" else table.c[column_name].desc()
        query = _sqa.select(id_col).where(*_clauses(criteria, base)).order_by(order_by).limit(n)
        stmt = _sqa.delete(base).where(id_col.in_(query))
        n_of_deleted_items = session.execute(stmt).rowcount
        return _text_response(f"{n_of_deleted_items} objects deleted from the database.")


@db_access_method
def exists(tenants: Tenants, base: type[_Base], criteria: Criteria = None) -> bool:
    """Check if an object with the given ID exists in the database."""
    source = _get_current_connection_source()
    table = base.__table__
    if criteria is None:
        criteria = {}
    with _Session(source) as session:
        clauses = [
            criteria[attr_label](getattr(table.columns, attr_label))
            for attr_label in criteria.keys()
        ]
        stmt = _sqa.select(_sqa.exists().where(*clauses))  # type: ignore
        stmt = _add_filter_by_tenant(session, stmt, base, tenants, require_single_tenant=False)
        result = bool(session.execute(stmt).scalar())
        return result


@db_access_method
def get_by_id(base: type[_Base], *ids: int, engine: Optional[_sqa.Engine] = None) -> list[_Base]:
    """Returns instances of the `base` with IDs from the `IDs` tuple.

    An optional `connection_source` may be specified to replace the otherwise used global connection
    source (an sqlalchemy Engine object).
    """
    engine = _get_current_connection_source(engine)
    with _Session(engine) as session, session.begin():
        try:
            results = []
            for id_value in ids:
                result = session.get(base, id_value)
                if result is not None:
                    results.append(result.copy())
            return results
        except _NoResultFound as e:
            raise _NoResultFound(f"{base.model_name} with ID={id_value} not found. {e}")


@db_access_method
def get_tenants(
    accessible_tenants: Tenants,
    connection_source: Optional[_sqa.Engine] = None,
) -> list[_TenantDB]:
    """Get tenants from the database corresponding to the tenant names in accessible tenants.

    If the accessible tenants are unrestricted, all tenants are returned.
    """
    global _wait_mg
    source = _get_current_connection_source(connection_source)
    with _Session(source) as session, session.begin():
        if accessible_tenants.unrestricted:
            tenant_objs: list[_TenantDB] = list(session.scalars(_sqa.select(_TenantDB)).all())
        else:
            tenant_names = _tenants_to_filter_by(accessible_tenants)
            tenant_stmt = _sqa.select(_TenantDB).where(_TenantDB.name.in_(tenant_names))
            tenant_objs: list[_TenantDB] = list(session.execute(tenant_stmt).scalars().all())
        tenants: list[_TenantDB] = [tenant.copy() for tenant in tenant_objs]
        return tenants


@db_access_method
def get(
    tenants: Tenants,
    base: type[_Base],
    first_n: int = 0,
    sort_result_by: Optional[dict[ColumnName, Order]] = None,
    criteria: Criteria = None,
    wait: bool = False,
    timeout_ms: Optional[int] = None,
    omitted_relationships: Optional[list[_InstrumentedAttribute]] = None,
    connection_source: Optional[_sqa.Engine] = None,
) -> list[Any]:
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
    source = _get_current_connection_source(connection_source)
    result = []
    with _Session(source) as session, session.begin():
        stmt = _sqa.select(base)
        stmt = _add_criteria_to_statement(stmt, base, criteria)
        stmt = _add_filter_by_tenant(session, stmt, base, tenants, require_single_tenant=False)
        stmt = _sort_results(stmt, base, sort_result_by)
        if first_n > 0:
            stmt = stmt.limit(first_n)
        if omitted_relationships is not None:
            for item in omitted_relationships:
                stmt = stmt.options(_noload(item))
        items = session.scalars(stmt).all()
        result = [item.copy() for item in items]
    if not result and wait:
        result = _wait_mg.wait_for_content(
            base.__tablename__,
            timeout_ms,
            validation=_functools.partial(_is_awaited_result_valid, criteria),
        )
    return result


def _add_criteria_to_statement(
    stmt: _sqa.Select, base: type[_Base], criteria: Criteria
) -> _sqa.Select:
    return stmt.where(*_clauses(criteria, base))


def _check_before_add(session: _Session, checked: Iterable[CheckBeforeAdd]) -> _Response:
    for obj in checked:
        try:
            obj.check(session)
        except _NoResultFound:
            msg = f"{obj._base.model_name} (ID={obj._id}) does not exist in the database."
            return _error(404, msg, "Cannot create object as some referenced objects do not exist.")
    return _json_response([])


def _clauses(criteria: Criteria, base: type[_Base]) -> list:
    if criteria is None:
        criteria = {}
    return [criteria[name](getattr(base.__table__.columns, name)) for name in criteria.keys()]


def get_children(
    parent_base: type[_Base],
    parent_id: int,
    children_col_name: str,
    connection_source: Optional[_sqa.Engine] = None,
    criteria: Criteria = None,
) -> list[_Base]:
    """Get children of an instance of an ORM mapped class `parent_base` with `parent_id` from its `children_col_name`.

    - `children_col_name` is the name of the relationship attribute in the parent_base class.

    - An optional `connection_source` may be specified to replace the otherwise used global connection source
    (an sqlalchemy Engine object).
    """
    source = _get_current_connection_source(connection_source)
    if criteria is None:
        criteria = {}
    with _Session(source) as session:
        try:
            raw_children = getattr(session.get_one(parent_base, parent_id), children_col_name)
            children = [
                child
                for child in raw_children
                if all(crit(getattr(child, attr)) for attr, crit in criteria.items())
            ]
            return children
        except _NoResultFound as e:
            raise ParentNotFound(
                f"Parent with ID={parent_id} not found in table {parent_base.__tablename__}. {e}"
            )


@db_access_method
def update(tenants: Tenants, *updated: _Base) -> _Response:
    """Updates an existing record in the database with the same ID as the updated_obj.

    The updated_obj is an instance of the ORM mapped class related to a table in database.
    """
    if not updated:
        return _text_response("Empty request body. Nothing to update in the database.")
    source = _get_current_connection_source()
    if updated[0].owned_by_tenant():
        response = _check_and_set_tenant(tenants, *updated)
        if response.status_code != 200:
            return response
    with _Session(source) as session, session.begin():
        try:
            for item in updated:
                session.get_one(item.__class__, item.id)
                session.merge(
                    item
                )  # copies updated item onto the item already existing in the database
            return _json_response(updated)
        except _sqaexc.IntegrityError as e:
            response = _error(400, str(e.orig), title="Cannot update object with invalid data")
        except _sqaexc.NoResultFound as e:
            msg = f"{item.model_name} (ID={item.id}) was not found. Nothing to update."
            response = _error(404, msg, title="Cannot update nonexistent object")
        except Exception as e:
            response = _error(500, str(e), title="Cannot update object due to unexpected error")
        session.rollback()
        return response


def db_object_check(
    base: type[_Base], id_: int, *conditions: _AttributeCondition, allow_nonexistence: bool = False
) -> CheckBeforeAdd:
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
    return CheckBeforeAdd(base, id_, *conditions, nullable=allow_nonexistence)


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
    _wait_mg.set_default_timeout(timeout_ms)


def _tenants_to_filter_by(tenants: Tenants) -> list[str]:
    return [tenants.current] if tenants.current else tenants.all


def _add_filter_by_tenant(
    session: _Session,
    stmt: _sqa.Select,
    base: type[_Base],
    tenants: Tenants,
    require_single_tenant: bool = True,
) -> _sqa.Select:
    if tenants is _NO_TENANTS or tenants.unrestricted:
        return stmt

    tenant_names = _tenants_to_filter_by(tenants)

    if require_single_tenant and len(tenant_names) != 1:
        raise ValueError(f"{len(tenant_names)} tenants provided, but only one is expected.")

    tenant_stmt = _sqa.select(_TenantDB).where(_TenantDB.name.in_(tenant_names))
    tenant_objs = session.execute(tenant_stmt).scalars().all()
    ids = [tenant.id for tenant in tenant_objs]
    if "tenant_id" in base.__table__.c:
        stmt = stmt.where(base.__table__.c["tenant_id"].in_(ids))
    return stmt


def _check_common_base_for_all_objs(*objs: _Base) -> None:
    """Check if all the `objs` are instances of the same ORM mapped class.

    If not, raise TypeError, otherwise do nothing.
    """
    if objs and any(obj.__tablename__ != objs[0].__tablename__ for obj in objs[1:]):
        raise TypeError("Object being added to database must belong to the same table.")


def _is_awaited_result_valid(result_attr_criteria: Criteria, item: Any) -> bool:
    """Return True if the `item` meets all the conditions expressed by the `attribute_criteria`"""
    if not result_attr_criteria:
        result_attr_criteria = {}
    return all(
        _criterion(item, criterion, attr_label)
        for attr_label, criterion in result_attr_criteria.items()
    )


def _criterion(item: Any, func: Callable[[Any], bool], item_attr_name: str) -> bool:
    """Return True if the `item` meets the condition expressed by the `func`"""
    return hasattr(item, item_attr_name) and func(item.__dict__[item_attr_name])


def _set_id_to_none(db_model_instances: list[_Base]) -> None:
    """Set "id" attribute of all the db_model_instances to None."""
    for obj in db_model_instances:
        obj.id = None  # type: ignore


def _sort_results(
    stmt: _sqa.Select,
    base: type[_Base],
    sort_result_by: Optional[dict[ColumnName, Order]] = None,
) -> _sqa.Select:
    if sort_result_by is None:
        sort_result_by = {}
    for attr_label, order in sort_result_by.items():
        if order not in ["asc", "desc"]:
            continue  # skip invalid order
        column = base.__table__.c.get(attr_label, None)
        if column is not None:
            order_by = column.asc() if order == "asc" else column.desc()
            stmt = stmt.order_by(order_by)
    return stmt


def _check_and_set_tenant(tenants: Tenants, *objs: _Base) -> _Response:
    """Check if the tenant exists and set the `tenant` attribute to all the `objs`."""
    if not (objs and objs[0].owned_by_tenant()):
        return _json_response([])

    if tenants is _NO_TENANTS:
        msg = f"Database model {objs[0].__class__.__name__} does not have a 'tenant_id' attribute."
        return _error(500, msg, title="Unexpected error when accessing database.")

    if not tenants.current:
        return _error(400, "Tenant not received in the request.", title="Tenant not received.")

    tenants_db: list[_TenantDB] = get(
        _NO_TENANTS, _TenantDB, criteria={"name": lambda x: x == tenants.current}
    )
    if not tenants_db:
        msg = f"Tenant '{tenants.current}' does not exist in the database."
        return _error(404, msg, title="Tenant not found.")

    for obj in objs:
        obj.tenant_id = tenants_db[0].id  # type: ignore
    return _json_response([])


def _set_tenant_id_to_all_objs(tenant_name: str, *objs: _Base) -> int:
    """Set tenant_id attribute to all the objs."""
    if not hasattr(objs[0], "tenant_id"):
        return 200
    id_ = _get_tenant_id(tenant_name)
    if id_ is None:
        return 401  # tenant does not exist
    else:
        for obj in objs:
            obj.__setattr__("tenant_id", id_)
        return 200


def _get_tenant_id(tenant_name: str) -> int | None:
    """Get tenant ID from the database by its name.

    If the tenant does not exist, return None.
    """
    criteria = {"name": lambda x: x == tenant_name}
    tenants: list[_TenantDB] = get(_NO_TENANTS, _TenantDB, criteria=criteria)
    if not tenants:
        return None
    return tenants[0].id
