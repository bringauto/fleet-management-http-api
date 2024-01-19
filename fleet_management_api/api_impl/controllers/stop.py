from typing import List

import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.api_impl.api_logging import log_and_respond, log_info
from fleet_management_api.models.stop import Stop
import fleet_management_api.database.db_access as db_access
import fleet_management_api.api_impl.obj_to_db as obj_to_db
from fleet_management_api.database.db_models import StopDBModel


def create_stop(stop) -> ConnexionResponse:
    if not connexion.request.is_json:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
    else:
        stop = Stop.from_dict(connexion.request.get_json())
        stop_db_model = obj_to_db.stop_to_db_model(stop)
        response = db_access.add_record(StopDBModel, stop_db_model)
        if response.status_code == 200:
            return log_and_respond(200, f"Stop (id={stop.id}, name='{stop.name}) has been sent.")
        elif response.status_code == 400:
            return log_and_respond(response.status_code, f"Stop (id={stop.id}, name='{stop.name}) could not be sent. {response.body}")
        else:
            return log_and_respond(response.status_code, response.body)


def delete_stop(stop_id: int) -> ConnexionResponse:
    response = db_access.delete_record(StopDBModel, id_name="id", id_value=stop_id)
    if response.status_code == 200:
        return log_and_respond(200, f"Stop with id={stop_id} has been deleted.")
    elif response.status_code == 404:
        return log_and_respond(404, f"Stop with id={stop_id} was not found.")
    else:
        return log_and_respond(response.status_code, f"Could not delete stop (id={stop_id}). {response.json()}")


def get_stop(stop_id: int) -> ConnexionResponse:
    stop_db_models = db_access.get_records(StopDBModel, equal_to={"id": stop_id})
    stops = [obj_to_db.stop_from_db_model(stop_db_model) for stop_db_model in stop_db_models]
    if len(stops) == 0:
        return log_and_respond(404, f"Stop with id={stop_id} was not found.")
    else:
        log_info(f"Found {len(stops)} stop with id={stop_id}")
        return ConnexionResponse(body=stops[0], status_code=200, content_type="application/json")


def get_stops() -> ConnexionResponse:
    stop_db_models = db_access.get_records(StopDBModel)
    stops: List[Stop] = [obj_to_db.stop_from_db_model(stop_db_model) for stop_db_model in stop_db_models]
    return ConnexionResponse(body=stops, status_code=200, content_type="application/json")


def update_stop(stop) -> ConnexionResponse:
    if connexion.request.is_json:
        stop = Stop.from_dict(connexion.request.get_json())
        stop_db_model = obj_to_db.stop_to_db_model(stop)
        response = db_access.update_record(updated_obj=stop_db_model)
        if 200 <= response.status_code < 300:
            log_info(f"Stop (id={stop.id} has been succesfully updated.")
            return ConnexionResponse(status_code=response.status_code, content_type="application/json", body=stop)
        elif response.status_code == 404:
            return log_and_respond(404, f"Stop (id={stop.id}) was not found and could not be updated. {response.body}")
        else:
            return log_and_respond(response.status_code, f"Stop (id={stop.id}) could not be updated. {response.body}")
    else:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required.")
