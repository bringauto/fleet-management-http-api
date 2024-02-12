import connexion  # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access


def add_car_state() -> _Response:
    """Post new car state.

    :param car_state: Car state to be added.

    :rtype: CarState

    The state must have a unique id.
    The car defined by 'car_id' must exist.
    """
    if not connexion.request.is_json:
        code, msg = 400, f"Invalid request format: {connexion.request.data}. JSON is required"
        _api.log_error(msg)
    else:
        car_state = _models.CarState.from_dict(connexion.request.get_json())  # noqa: E501
        state_db_model = _api.car_state_to_db_model(car_state)
        response = _db_access.add(
            state_db_model,
            check_reference_existence={_db_models.CarDBModel: car_state.car_id},
        )
        if response.status_code == 200:
            inserted_model = _api.car_state_from_db_model(response.body)
            code, msg = 200, f"Car state (id={inserted_model.id}) was succesfully created."
            _api.log_info(msg)
            cleanup_response = _remove_old_states(car_state.car_id)
            if cleanup_response.status_code != 200:
                code, cleanup_error_msg = cleanup_response.status_code, cleanup_response.body
                _api.log_error(cleanup_error_msg)
                msg = msg + "\n" + cleanup_error_msg
            else:
                return _Response(
                    body=inserted_model, status_code=200, content_type="application/json"
                )
        else:
            code, msg = (
                response.status_code,
                f"Car state could not be sent. {response.body}",
            )
            _api.log_error(msg)
    return _Response(body=msg, status_code=code)


def get_all_car_states() -> _Response:
    """Get all car states for all the cars."""
    car_state_db_models = _db_access.get(_db_models.CarStateDBModel)
    car_states = [
        _api.car_state_from_db_model(car_state_db_model)
        for car_state_db_model in car_state_db_models
    ]
    return _Response(body=car_states, status_code=200, content_type="application/json")


def get_car_states(car_id: int, all_available: bool = False) -> _Response:
    """Get all car states for a car idenfified by 'car_id' of an existing car."""
    try:
        car_state_db_models = _db_access.get_children(_db_models.CarDBModel, car_id, "states")
        if not all_available and car_state_db_models:
            car_state_db_models = [car_state_db_models[-1]]
        car_states = [_api.car_state_from_db_model(car_state_db_model) for car_state_db_model in car_state_db_models]  # type: ignore
        return _Response(body=car_states, status_code=200, content_type="application/json")
    except _db_access.ParentNotFound as e:
        return _api.log_and_respond(404, f"Car with id={car_id} not found. {e}")
    except Exception as e:  # pragma: no cover
        return _api.log_and_respond(500, f"Error: {e}")


def _remove_old_states(car_id: int) -> _Response:
    car_state_db_models = _db_access.get(
        _db_models.CarStateDBModel, criteria={"car_id": lambda x: x == car_id}
    )
    curr_n_of_states = len(car_state_db_models)
    delta = curr_n_of_states - _db_models.CarStateDBModel.max_n_of_stored_states()
    if delta > 0:
        response = _db_access.delete_n(
            _db_models.CarStateDBModel,
            delta,
            column_name="timestamp",
            start_from="minimum",
            criteria={"car_id": lambda x: x == car_id},
        )
        return _Response(response.status_code, response.body)
    else:
        return _Response(status_code=200, content_type="text/plain", body="")
