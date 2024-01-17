import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models.car_state import CarState
import fleet_management_api.api_impl.db_models as db_models
import fleet_management_api.database.db_access as db_access
from fleet_management_api.api_impl.api_logging import log_info, log_error


def add_car_state(car_state):  # noqa: E501
    if not connexion.request.is_json:
        code, msg = 400, f"Invalid request format: {connexion.request.data}. JSON is required"
        log_error(msg)
    else:
        car_state = CarState.from_dict(connexion.request.get_json())  # noqa: E501
        state_db_model = db_models.car_state_to_db_model(car_state)
        car_db_model = db_access.get_records(db_models.CarDBModel, equal_to={'id': car_state.car_id})
        if len(car_db_model) == 0:
            code, msg = 404, f"Car with id='{car_state.car_id}' was not found."
            log_error(msg)
        else:
            response = db_access.add_record(db_models.CarStateDBModel, state_db_model)
            if response.status_code == 200:
                code, msg = 200, f"Car state with id='{car_state.id}' was succesfully created."
                log_info(msg)
            else:
                code, msg = response.status_code, f"Car state with id='{car_state.id}' could not be sent. {response.body}",
                log_error(msg)

    return ConnexionResponse(body=msg, status_code=code)