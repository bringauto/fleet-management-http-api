from typing import List

import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.api_impl.api_logging import log_and_respond, log_info
from fleet_management_api.models import Route
import fleet_management_api.api_impl.obj_to_db as obj_to_db
import fleet_management_api.database.db_access as db_access
from fleet_management_api.database.db_models import RouteDBModel


def create_route(route: Route) -> ConnexionResponse:
    if not connexion.request.is_json:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
    else:
        route = Route.from_dict(connexion.request.get_json())
        route_db_model = obj_to_db.route_to_db_model(route)
        response = db_access.add_record(RouteDBModel, route_db_model)
        if response.status_code == 200:
            return log_and_respond(200, f"Route (id={route.id}, name='{route.name}) has been sent.")
        elif response.status_code == 400:
            return log_and_respond(response.status_code, f"Route (id={route.id}, name='{route.name}) could not be sent. {response.body}")
        else:
            return log_and_respond(response.status_code, response.body)


def delete_route(route_id: int) -> ConnexionResponse:
    return ConnexionResponse(body="Not implemented", status_code=501, mimetype='text/plain')


def get_route(route_id: int) -> Route:
    route_db_models = db_access.get_records(RouteDBModel, equal_to={"id": route_id})
    routes = [obj_to_db.route_from_db_model(route_db_model) for route_db_model in route_db_models]
    if len(routes) == 0:
        return log_and_respond(404, f"Route with id={route_id} was not found.")
    else:
        log_info(f"Found {len(routes)} route with id={route_id}")
        return ConnexionResponse(body=routes[0], status_code=200, content_type="application/json")


def get_routes() -> List[Route]:
    route_db_models = db_access.get_records(RouteDBModel)
    route: List[Route] = [obj_to_db.platform_hw_id_from_db_model(route_db_model) for route_db_model in route_db_models]
    return ConnexionResponse(body=route, status_code=200, content_type="application/json")


def update_route(route_id: int, route: Route) -> ConnexionResponse:
    return ConnexionResponse(body="Not implemented", status_code=501, mimetype='text/plain')
