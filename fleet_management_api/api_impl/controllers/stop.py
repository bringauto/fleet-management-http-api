from typing import List, Dict

import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response # type: ignore

import fleet_management_api.api_impl as _api
from fleet_management_api.models.stop import Stop as _Stop
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models


def create_stop(stop: Dict|_Stop) -> _Response:
    """Post a new stop. The stop must have a unique id."""
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
    else:
        stop = _Stop.from_dict(connexion.request.get_json())
        stop_db_model = _api.stop_to_db_model(stop)
        response = _db_access.add(_db_models.StopDBModel, stop_db_model)
        if response.status_code == 200:
            return _api.log_and_respond(200, f"Stop (id={stop.id}, name='{stop.name}) has been created.")
        else:
            return _api.log_and_respond(response.status_code, f"Stop (id={stop.id}, name='{stop.name}) could not be sent. {response.body}")


def delete_stop(stop_id: int) -> _Response:
    """Delete an existing stop identified by 'stop_id'.

    The stop cannot be deleted if it is referenced by any route.
    """
    routes_response = _get_routes_referencing_stop(stop_id)
    if routes_response.status_code != 200:
        return _api.log_and_respond(routes_response.status_code, routes_response.body)
    response = _db_access.delete(_db_models.StopDBModel, stop_id)
    if response.status_code == 200:
        return _api.log_and_respond(200, f"Stop with id={stop_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _api.log_and_respond(response.status_code, f"Could not delete stop with id={stop_id}{note}. {response.body}")


def get_stop(stop_id: int) -> _Response:
    """Get an existing stop identified by 'stop_id'."""
    stop_db_models: List[_db_models.StopDBModel] = _db_access.get(_db_models.StopDBModel, criteria={"id": lambda x: x==stop_id})
    stops = [_api.stop_from_db_model(stop_db_model) for stop_db_model in stop_db_models]
    if len(stops) == 0:
        return _api.log_and_respond(404, f"Stop with id={stop_id} was not found.")
    else:
        _api.log_info(f"Found {len(stops)} stop with id={stop_id}")
        return _Response(body=stops[0], status_code=200, content_type="application/json")


def get_stops() -> _Response:
    """Get all existing stops."""
    stop_db_models = _db_access.get(_db_models.StopDBModel)
    stops: List[_Stop] = [_api.stop_from_db_model(stop_db_model) for stop_db_model in stop_db_models]
    _api.log_info(f"Found {len(stops)} stops.")
    return _Response(body=stops, status_code=200, content_type="application/json")


def update_stop(stop: Dict|_Stop) -> _Response:
    """Update an existing stop."""
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required.")
    else:
        stop = _Stop.from_dict(connexion.request.get_json())
        stop_db_model = _api.stop_to_db_model(stop)
        response = _db_access.update(stop_db_model)
        if response.status_code == 200:
            _api.log_info(f"Stop (id={stop.id} has been succesfully updated.")
            return _Response(status_code=response.status_code, content_type="application/json", body=stop)
        else:
            note = " (not found)" if response.status_code == 404 else ""
            return _api.log_and_respond(response.status_code, f"Stop (id={stop.id}) could not be updated {note}. {response.body}")


def _get_routes_referencing_stop(stop_id: int) -> _Response:
    route_db_models = [m for m in _db_access.get(_db_models.RouteDBModel) if stop_id in m.stop_ids]
    if len(route_db_models) > 0:
        return _api.log_and_respond(400, f"Stop with id={stop_id} cannot be deleted because it is referenced by routes: {route_db_models}")
    else:
        return _api.log_and_respond(200, f"Stop with id={stop_id} is not referenced by any route.")

