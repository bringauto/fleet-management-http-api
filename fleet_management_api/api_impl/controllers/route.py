from typing import List

import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse # type: ignore

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
    response = db_access.delete_record(RouteDBModel, id_name="id", id_value=route_id)
    if response.status_code == 200:
        return log_and_respond(200, f"Route with id={route_id} has been deleted.")
    elif response.status_code == 404:
        return log_and_respond(404, f"Route with id={route_id} was not found.")
    else:
        return log_and_respond(response.status_code, f"Could not delete route (id={route_id}). {response.json()}")


def get_route(route_id: int) -> Route:
    route_db_models = db_access.get_records(RouteDBModel, criteria={"id": lambda x: x==route_id})
    routes = [obj_to_db.route_from_db_model(route_db_model) for route_db_model in route_db_models]
    if len(routes) == 0:
        return log_and_respond(404, f"Route with id={route_id} was not found.")
    else:
        log_info(f"Found {len(routes)} route with id={route_id}")
        return ConnexionResponse(body=routes[0], status_code=200, content_type="application/json")


def get_routes() -> List[Route]:
    route_db_models = db_access.get_records(RouteDBModel)
    route: List[Route] = [obj_to_db.route_from_db_model(route_db_model) for route_db_model in route_db_models]
    return ConnexionResponse(body=route, status_code=200, content_type="application/json")


def update_route(route: Route) -> ConnexionResponse:
    if connexion.request.is_json:
        route = Route.from_dict(connexion.request.get_json())
        route_db_model = obj_to_db.route_to_db_model(route)
        response = db_access.update_record(updated_obj=route_db_model)
        if 200 <= response.status_code < 300:
            log_info(f"Route (id={route.id} has been succesfully updated.")
            return ConnexionResponse(status_code=response.status_code, content_type="application/json", body=route)
        elif response.status_code == 404:
            return log_and_respond(404, f"Route (id={route.id}) was not found and could not be updated. {response.body}")
        else:
            return log_and_respond(response.status_code, f"Route (id={route.id}) could not be updated. {response.body}")
    else:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required.")