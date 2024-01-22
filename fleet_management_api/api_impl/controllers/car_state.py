import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models.car_state import CarState
import fleet_management_api.api_impl.obj_to_db as obj_to_db
import fleet_management_api.database.db_models as db_models
import fleet_management_api.database.db_access as db_access
from fleet_management_api.api_impl.api_logging import log_info, log_error, log_and_respond


def add_car_state(car_state) -> ConnexionResponse:
    if not connexion.request.is_json:
        code, msg = 400, f"Invalid request format: {connexion.request.data}. JSON is required"
        log_error(msg)
    else:
        car_state = CarState.from_dict(connexion.request.get_json())  # noqa: E501
        state_db_model = obj_to_db.car_state_to_db_model(car_state)
        car_db_model = db_access.get_records(db_models.CarDBModel, equal_to={'id': car_state.car_id})
        if len(car_db_model) == 0:
            code, msg = 404, f"Car with id='{car_state.car_id}' was not found."
            log_error(msg)
        else:
            response = db_access.add_record(db_models.CarStateDBModel, state_db_model)
            if response.status_code == 200:
                code, msg = 200, f"Car state with id='{car_state.id}' was succesfully created."
                log_info(msg)
                cleanup_response = _remove_old_states(car_state.car_id)
                if cleanup_response.status_code != 200:
                    code, cleanup_error_msg = cleanup_response.status_code, cleanup_response.body
                    log_error(cleanup_error_msg)
                    msg = msg + "\n" + cleanup_error_msg
            else:
                code, msg = response.status_code, f"Car state with id='{car_state.id}' could not be sent. {response.body}",
                log_error(msg)

    return ConnexionResponse(body=msg, status_code=code)


def get_all_car_states() -> ConnexionResponse:
    car_state_db_models = db_access.get_records(db_models.CarStateDBModel)
    car_states = [obj_to_db.car_state_from_db_model(car_state_db_model) for car_state_db_model in car_state_db_models]
    return ConnexionResponse(body=car_states, status_code=200, content_type="application/json")


def get_car_states(car_id: int, all_available: bool = False) -> ConnexionResponse:
    if not _car_exists(car_id):
        return log_and_respond(404, f"Car with id='{car_id}' was not found. Cannot get its state.")
    else:
        car_state_db_models = db_access.get_records(db_models.CarStateDBModel, equal_to={'car_id': car_id})
        if not all_available and car_state_db_models:
            car_state_db_models = [car_state_db_models[-1]]
        car_states = [obj_to_db.car_state_from_db_model(car_state_db_model) for car_state_db_model in car_state_db_models]
        return ConnexionResponse(body=car_states, status_code=200, content_type="application/json")


def _car_exists(car_id: int) -> bool:
    return bool(db_access.get_records(db_models.CarDBModel, equal_to={'id': car_id}))


def _remove_old_states(car_id: int) -> ConnexionResponse:
    car_state_db_models = db_access.get_records(db_models.CarStateDBModel, equal_to={'car_id': car_id})
    curr_n_of_states = len(car_state_db_models)
    delta = curr_n_of_states - db_models.CarStateDBModel.max_n_of_states
    if delta>0:
        response = db_access.delete_n_records(
            db_models.CarStateDBModel,
            delta,
            id_name="timestamp",
            start_from="minimum"
        )
        if response.status_code != 200:
            return log_and_respond(response.status_code, response.body)
        else:
            return log_and_respond(200, f"Removing oldest state from database (car id = {car_id}).")
    else:
        return ConnexionResponse(status_code=200, content_type="text/plain", body="")