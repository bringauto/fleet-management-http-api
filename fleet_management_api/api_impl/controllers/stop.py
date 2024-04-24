import connexion  # type: ignore

from fleet_management_api.models.stop import Stop as _Stop
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    error as _error
)
from fleet_management_api.api_impl.api_logging import (
    log_error_and_respond as _log_error_and_respond,
    log_info_and_respond as _log_info_and_respond,
    log_info as _log_info,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)


def create_stop() -> _Response:
    """Post a new stop. The stop must have a unique id."""
    if not connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        stop = _Stop.from_dict(connexion.request.get_json())
        stop_db_model = _obj_to_db.stop_to_db_model(stop)
        response = _db_access.add(stop_db_model)
        if response.status_code == 200:
            _log_info(f"Stop (ID={response.body[0].id}, name='{stop.name}) has been created.")
            return _json_response(_obj_to_db.stop_from_db_model(response.body[0]))
        else:
            return _error(
                response.status_code,
                f"Stop (name='{stop.name}) could not be created. {response.body['detail']}",
                title=response.body["title"],
            )


def delete_stop(stop_id: int) -> _Response:
    """Delete an existing stop identified by 'stop_id'.

    The stop cannot be deleted if it is referenced by any route.
    """
    routes_response = _get_routes_referencing_stop(stop_id)
    if routes_response.status_code != 200:
        return _log_error_and_respond(
            routes_response.body["title"],
            routes_response.status_code,
            routes_response.body["title"],
        )
    response = _db_access.delete(_db_models.StopDBModel, stop_id)
    if response.status_code == 200:
        return _log_info_and_respond(f"Stop with ID={stop_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _error(
            response.status_code,
            f"Could not delete stop with ID={stop_id}{note}. {response.body['detail']}",
            response.body["title"],
        )


def get_stop(stop_id: int) -> _Response:
    """Get an existing stop identified by 'stop_id'."""
    stop_db_models: list[_db_models.StopDBModel] = _db_access.get(
        _db_models.StopDBModel, criteria={"id": lambda x: x == stop_id}
    )
    stops = [_obj_to_db.stop_from_db_model(stop_db_model) for stop_db_model in stop_db_models]
    if len(stops) == 0:
        return _log_error_and_respond(
            f"Stop with ID={stop_id} was not found.", 404, title="Object not found"
        )
    else:
        _log_info(f"Found {len(stops)} stop with ID={stop_id}")
        return _Response(body=stops[0], status_code=200, content_type="application/json")


def get_stops() -> _Response:
    """Get all existing stops."""
    stop_db_models = _db_access.get(_db_models.StopDBModel)
    stops: list[_Stop] = [
        _obj_to_db.stop_from_db_model(stop_db_model) for stop_db_model in stop_db_models
    ]
    _log_info(f"Found {len(stops)} stops.")
    return _json_response(stops)


def update_stop(stop: dict | _Stop) -> _Response:
    """Update an existing stop."""
    if not connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        stop = _Stop.from_dict(connexion.request.get_json())
        stop_db_model = _obj_to_db.stop_to_db_model(stop)
        response = _db_access.update(stop_db_model)
        if response.status_code == 200:
            _log_info(f"Stop (ID={stop.id} has been succesfully updated.")
            return _json_response(stop)
        else:
            note = " (not found)" if response.status_code == 404 else ""
            return _log_error_and_respond(
                f"Stop (ID={stop.id}) could not be updated {note}. {response.body['detail']}",
                response.status_code,
                response.body["title"],
            )


def _get_routes_referencing_stop(stop_id: int) -> _Response:
    route_db_models = [m for m in _db_access.get(_db_models.RouteDBModel) if stop_id in m.stop_ids]
    if len(route_db_models) > 0:
        return _log_error_and_respond(
            f"Stop with ID={stop_id} cannot be deleted because it is referenced by routes: {route_db_models}.",
            400,
            title="Cannot delete object because it is referenced by other objects",
        )
    else:
        return _log_info_and_respond(f"Stop with ID={stop_id} is not referenced by any route.")
