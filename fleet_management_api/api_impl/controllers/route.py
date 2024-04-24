import connexion  # type: ignore

import fleet_management_api.models as _models
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
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


def create_route() -> _Response:
    """Post a new route. The route must have a unique id and all the stops identified by stop ids must exist."""
    if not connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        route = _models.Route.from_dict(connexion.request.get_json())
        check_response = _check_route_model(route)
        if not check_response.status_code == 200:
            return _log_error_and_respond(
                check_response.body["detail"],
                check_response.status_code,
                check_response.body["title"],
            )
        route_db_model = _obj_to_db.route_to_db_model(route)
        response = _db_access.add(route_db_model)
        if response.status_code == 200:
            inserted_db_model = response.body[0]
            route_visualization_response = _create_empty_route_visualization(inserted_db_model.id)
            if not route_visualization_response.status_code == 200:
                return route_visualization_response
            _log_info(f"Route (name='{route.name}) has been created.")
            return _json_response(_obj_to_db.route_from_db_model(inserted_db_model))
        else:
            return _log_error_and_respond(
                f"Route (name='{route.name}) could not be sent. {response.body['detail']}",
                response.status_code,
                response.body["title"],
            )


def delete_route(route_id: int) -> _Response:
    """Delete an existing route identified by 'route_id'."""
    related_orders_response = _find_related_orders(route_id)
    if not related_orders_response.status_code == 200:
        return _log_error_and_respond(
            related_orders_response.status_code,
            related_orders_response.status_code,
            related_orders_response.body,
        )
    response = _db_access.delete(_db_models.RouteDBModel, route_id)
    if not response.status_code == 200:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_error_and_respond(
            f"Could not delete route with ID={route_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
    else:
        route_deletion_msg = f"Route with ID={route_id} has been deleted."
        return _log_info_and_respond(route_deletion_msg)


def get_route(route_id: int) -> _models.Route:
    """Get an existing route identified by 'route_id'."""
    route_db_models = _db_access.get(
        _db_models.RouteDBModel, criteria={"id": lambda x: x == route_id}
    )
    routes = [_obj_to_db.route_from_db_model(route_db_model) for route_db_model in route_db_models]
    if len(routes) == 0:
        return _log_error_and_respond(
            f"Route with ID={route_id} was not found.", 404, title="Object not found"
        )
    else:
        _log_info(f"Found {len(routes)} route with ID={route_id}")
        return _json_response(routes[0])


def get_routes() -> list[_models.Route]:
    """Get all existing routes."""
    route_db_models = _db_access.get(_db_models.RouteDBModel)
    route: list[_models.Route] = [
        _obj_to_db.route_from_db_model(route_db_model) for route_db_model in route_db_models
    ]
    _log_info(f"Found {len(route)} routes.")
    return _json_response(route)


def update_route(route: dict | _models.Route) -> _Response:
    """Update an existing route identified by 'route_id'."""
    if not connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        route = _models.Route.from_dict(connexion.request.get_json())
        check_stops_response = _find_nonexistent_stops(route)
        if not check_stops_response.status_code == 200:
            return _log_error_and_respond(
                check_stops_response.body, check_stops_response.status_code, "Object not found"
            )
        route_db_model = _obj_to_db.route_to_db_model(route)
        response = _db_access.update(updated=route_db_model)
        if response.status_code == 200:
            _log_info(f"Route (ID={route.id} has been succesfully updated.")
            return _json_response(route)
        else:
            note = " (not found)" if response.status_code == 404 else ""
            return _log_error_and_respond(
                f"Route (ID={route.id}) could not be updated{note}. {response.body['detail']}",
                404,
                response.body["title"],
            )


def _check_route_model(route: _models.Route) -> _Response:
    check_stops_response = _find_nonexistent_stops(route)
    if not check_stops_response.status_code == 200:
        return check_stops_response
    return _text_response(f"Route (ID={route.id}, name='{route.name}) has been checked.")


def _create_empty_route_visualization(route_id: int) -> _Response:
    response = _db_access.add(
        _db_models.RouteVisualizationDBModel(id=route_id, route_id=route_id, points=[]),
    )
    if not response.status_code == 200:
        return _error(
            response.status_code,
            f"Could not create route visualization for route with ID={route_id}. {response.body['detail']}",
            response.body["title"],
        )
    else:
        return _text_response(f"Empty route visualization (route ID={route_id}) has been created.")


def _find_nonexistent_stops(route: _models.Route) -> _Response:
    checked_id_set: set[int] = set(route.stop_ids)
    existing_ids = set([stop_id.id for stop_id in _db_access.get(_db_models.StopDBModel)])
    nonexistent_stop_ids = checked_id_set.difference(existing_ids)
    if nonexistent_stop_ids:
        return _error(
            404,
            f"Route (ID={route.id}, name='{route.name}) has not been created - some of the required stops do not exist. "
            f"Nonexstent stop ids: {nonexistent_stop_ids}",
            title="Object not found",
        )
    else:
        return _text_response(f"Route (ID={route.id}, name='{route.name}) has been checked.")


def _find_related_orders(route_id: int) -> _Response:
    related_orders = _db_access.get(
        _db_models.OrderDBModel, criteria={"stop_route_id": lambda x: x == route_id}
    )
    if related_orders:
        return _error(
            400,
            f"Route (ID={route_id}) could not be deleted, because there are orders related to it. "
            f"Related orders: {related_orders}",
            title="Cannot delete object as other objects depend on it",
        )
    else:
        return _text_response(f"Route (ID={route_id}) has been checked.")
