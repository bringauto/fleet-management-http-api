from typing import List, Set

import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response # type: ignore

import fleet_management_api.api_impl  as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import RouteDBModel as _RouteDBModel
from fleet_management_api.database.db_models import RoutePointsDBModel as _RoutePointsDBModel
from fleet_management_api.database.db_models import StopDBModel as _StopDBModel


def create_route(route: _models.Route) -> _Response:
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
    else:
        route = _models.Route.from_dict(connexion.request.get_json())
        check_response = _check_route_model(route)
        if not check_response.status_code == 200:
            return check_response

        route_db_model = _api.route_to_db_model(route)
        response = _db_access.add(_RouteDBModel, route_db_model)
        if not response.status_code == 200:
            return _api.log_and_respond(response.status_code, f"Route (id={route.id}, name='{route.name}) could not be sent. {response.body}")
        else:
            return _api.log_and_respond(200, f"Route (id={route.id}, name='{route.name}) has been sent.")


def delete_route(route_id: int) -> _Response:
    response = _db_access.delete(_RouteDBModel, id_name="id", id_value=route_id)
    if response.status_code == 200:
        return _api.log_and_respond(200, f"Route with id={route_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _api.log_and_respond(response.status_code, f"Could not delete route with id={route_id}{note}. {response.body}")


def get_route(route_id: int) -> _models.Route:
    route_db_models = _db_access.get(_RouteDBModel, criteria={"id": lambda x: x==route_id})
    routes = [_api.route_from_db_model(route_db_model) for route_db_model in route_db_models]
    if len(routes) == 0:
        return _api.log_and_respond(404, f"Route with id={route_id} was not found.")
    else:
        _api.log_info(f"Found {len(routes)} route with id={route_id}")
        return _Response(body=routes[0], status_code=200, content_type="application/json")


def get_routes() -> List[_models.Route]:
    route_db_models = _db_access.get(_RouteDBModel)
    route: List[_models.Route] = [_api.route_from_db_model(route_db_model) for route_db_model in route_db_models]
    return _Response(body=route, status_code=200, content_type="application/json")


def update_route(route: _models.Route) -> _Response:
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required.")
    else:
        route = _models.Route.from_dict(connexion.request.get_json())

        check_stops_response = _find_nonexistent_stops(route)
        if not check_stops_response.status_code == 200:
            return check_stops_response

        route_db_model = _api.route_to_db_model(route)
        response = _db_access.update(updated_obj=route_db_model)
        if response.status_code == 200:
            _api.log_info(f"Route (id={route.id} has been succesfully updated.")
            return _Response(status_code=response.status_code, content_type="application/json", body=route)
        else:
            note = " (not found)" if response.status_code == 404 else ""
            return _api.log_and_respond(404, f"Route (id={route.id}) was not found and could not be updated{note}. {response.body}")


def _check_route_model(route: _models.Route) -> _Response:
    route_points_response = _create_empty_route_points_list(route)
    if not route_points_response.status_code == 200:
        return route_points_response
    check_stops_response = _find_nonexistent_stops(route)
    if not check_stops_response.status_code == 200:
        return check_stops_response
    return _Response(status_code=200, content_type="text/plain", body=f"Route (id={route.id}, name='{route.name}) has been checked.")


def _create_empty_route_points_list(route: _models.Route) -> _Response:
    response = _db_access.add(_RoutePointsDBModel, _RoutePointsDBModel(id=route.id, route_id=route.id, points=[]))
    if not response.status_code == 200:
        return _Response(
            response.status_code,
            content_type="text/plain",
            body=f"Could not create route point for route with id={route.id}, name='{route.name}'."
                 f"{response.body}")
    else:
        return _Response(status_code=200, content_type="text/plain", body=f"Empty list of route points for route with id={route.id}, name='{route.name}' has been created.")


def _find_nonexistent_stops(route: _models.Route) -> _Response:
    checked_id_set: Set[int] = set(route.stop_ids)
    existing_ids = set([stop_id.id for stop_id in _db_access.get(_StopDBModel)])
    nonexistent_stop_ids = checked_id_set.difference(existing_ids)
    if nonexistent_stop_ids:
        return _Response(
            status_code=404,
            content_type="text/plain",
            body=f"Route (iid={route.id}, name='{route.name}) has been sent, but some of its stops do not exist."
                 f"Nonexstent stop ids: {nonexistent_stop_ids}")
    else:
        return _Response(status_code=200, content_type="text/plain", body=f"Route (id={route.id}, name='{route.name}) has been sent.")