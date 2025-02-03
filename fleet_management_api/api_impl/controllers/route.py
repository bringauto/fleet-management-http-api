from functools import partial

from fleet_management_api.models import (
    Route as _Route,
)
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import (
    OrderDB as _OrderDB,
    RouteDB as _RouteDB,
    RouteVisualizationDB as _RouteVisDB,
    StopDB as _StopDB,
)
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    error as _error,
    text_response as _text_response,
)
from fleet_management_api.api_impl.api_logging import (
    log_error_and_respond as _log_error_and_respond,
    log_info_and_respond as _log_info_and_respond,
    log_info as _log_info,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
from fleet_management_api.response_consts import (
    CANNOT_DELETE_REFERENCED as _CANNOT_DELETE_REFERENCED,
    OBJ_NOT_FOUND as _OBJ_NOT_FOUND,
)
from fleet_management_api.api_impl.load_request import (
    RequestJSON as _RequestJSON,
    RequestEmpty as _RequestEmpty,
)
from fleet_management_api.api_impl.tenants import AccessibleTenants as _AccessibleTenants


def create_routes() -> _Response:
    """Post a new route.

    If some of the routes' creation fails, no routes are added to the server.

    The route creation can succeed only if:
    - all stops exist,
    - there is not a route with the same name.
    """
    request = _RequestJSON.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    routes = [_Route.from_dict(r) for r in request.data]
    for r in routes:
        check_response = _check_route_model(tenants, r)
        if check_response.status_code != 200:
            return _log_error_and_respond(
                check_response.body["detail"],
                check_response.status_code,
                check_response.body["title"],
            )

    route_db_models = [_obj_to_db.route_to_db_model(r) for r in routes]
    response = _db_access.add(tenants, *route_db_models)
    if response.status_code == 200:
        inserted_db_models: list[_RouteDB] = response.body
        for route in inserted_db_models:
            assert route.id is not None
            _create_empty_route_visualization(tenants, route.id)
            _log_info(f"Route (name='{route.name}) has been created.")
        return _json_response([_obj_to_db.route_from_db_model(m) for m in inserted_db_models])
    else:
        return _log_error_and_respond(
            f"Routes could not be created. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )


def delete_route(route_id: int) -> _Response:
    """Delete an existing route identified by 'route_id'."""
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    related_orders_response = _find_related_orders(tenants, route_id)
    if related_orders_response.status_code != 200:
        return _log_error_and_respond(
            related_orders_response.status_code,
            related_orders_response.status_code,
            related_orders_response.body,
        )
    response = _db_access.delete(tenants, _RouteDB, route_id)
    if response.status_code != 200:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_error_and_respond(
            f"Could not delete route with ID={route_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
    else:
        route_deletion_msg = f"Route with ID={route_id} has been deleted."
        return _log_info_and_respond(route_deletion_msg)


def get_route(route_id: int) -> _Route:
    """Get an existing route identified by 'route_id'."""
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    route_db_models = _db_access.get(tenants, _RouteDB, criteria={"id": lambda x: x == route_id})
    routes = [_obj_to_db.route_from_db_model(route_db_model) for route_db_model in route_db_models]
    if len(routes) == 0:
        return _log_error_and_respond(
            f"Route with ID={route_id} was not found.", 404, title=_OBJ_NOT_FOUND
        )
    else:
        _log_info(f"Found {len(routes)} route with ID={route_id}")
        return _json_response(routes[0])


def get_routes() -> list[_Route]:
    """Get all existing routes."""
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    route_db_models = _db_access.get(tenants, _RouteDB)
    route: list[_Route] = [
        _obj_to_db.route_from_db_model(route_db_model) for route_db_model in route_db_models
    ]
    _log_info(f"Found {len(route)} routes.")
    return _json_response(route)


def update_routes() -> _Response:
    """Update an existing route identified by 'route_ids' array.

    If some of the routes' update fails, no routes are updated on the server.

    The route update can succeed only if:
    - all stops exist,
    - all route IDs exist.
    """
    request = _RequestJSON.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    routes = [_Route.from_dict(item) for item in request.data]
    check_stops_response = _find_nonexistent_stops(tenants, *routes)
    if check_stops_response.status_code != 200:
        return _log_error_and_respond(
            check_stops_response.body,
            check_stops_response.status_code,
            _OBJ_NOT_FOUND,
        )
    route_db_models = [_obj_to_db.route_to_db_model(r) for r in routes]
    response = _db_access.update(tenants, *route_db_models)
    if response.status_code == 200:
        inserted_routes: list[_RouteDB] = response.body
        for r in inserted_routes:
            _log_info(f"Route (ID={r.id} has been succesfully updated.")
        return _text_response("Routes were succesfully updated.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_error_and_respond(
            f"Routes {[r.name for r in routes]} could not be updated {note}. {response.body['detail']}",
            404,
            response.body["title"],
        )


def _check_route_model(tenants: _AccessibleTenants, route: _Route) -> _Response:
    check_stops_response = _find_nonexistent_stops(tenants, route)
    if check_stops_response.status_code != 200:
        return check_stops_response
    return _text_response(f"Route (ID={route.id}, name='{route.name}) has been checked.")


def _create_empty_route_visualization(tenants: _AccessibleTenants, route_id: int) -> _Response:
    response = _db_access.add(
        tenants,
        _RouteVisDB(id=route_id, route_id=route_id, points=[], hexcolor="#00BCF2"),
    )
    if response.status_code != 200:
        return _error(
            response.status_code,
            f"Could not create route visualization for route with ID={route_id}. {response.body['detail']}",
            response.body["title"],
        )
    else:
        return _text_response(f"Empty route visualization (route ID={route_id}) has been created.")


def _find_nonexistent_stops(tenants: _AccessibleTenants, *routes: _Route) -> _Response:
    for route in routes:
        checked_id_set: set[int] = set(route.stop_ids)
        for id_ in checked_id_set:
            def check_id(x: int, id_: int) -> bool:
                return x == id_
            _db_access.exists(tenants, _StopDB, criteria={"id": partial(check_id, id_=id_)})
        existing_ids = set([stop_id.id for stop_id in _db_access.get(tenants, _StopDB)])
        nonexistent_stop_ids = checked_id_set.difference(existing_ids)
        if nonexistent_stop_ids:
            return _error(
                404,
                f"Route (ID={route.id}, name='{route.name}) has not been created - some of the required stops do not exist. "
                f"Nonexstent stop ids: {nonexistent_stop_ids}",
                title=_OBJ_NOT_FOUND,
            )
        else:
            return _text_response(f"Route (ID={route.id}, name='{route.name}) has been checked.")


def _find_related_orders(tenants: _AccessibleTenants, route_id: int) -> _Response:
    related_orders = _db_access.get(
        tenants, _OrderDB, criteria={"stop_route_id": lambda x: x == route_id}
    )
    if related_orders:
        return _error(
            400,
            f"Route (ID={route_id}) could not be deleted, because there are orders related to it. "
            f"Related orders: {related_orders}",
            title=_CANNOT_DELETE_REFERENCED,
        )
    else:
        return _text_response(f"Route (ID={route_id}) has been checked.")
