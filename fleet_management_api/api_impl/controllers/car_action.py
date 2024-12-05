from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

from fleet_management_api.models.car_action_state import CarActionState  # noqa: E501
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.api_impl.obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_responses import (
    json_response as _json_response,
    error as _error,
)
from fleet_management_api.api_impl.api_logging import log_info as _log_info, log_error as _log_error


def get_car_action_states(
    car_id: int, since: int = 0, wait: bool = False, last_n: int = 0
) -> _Response:
    """Finds car action states for a Car with given carId.

     # noqa: E501


    :rtype: ConnexionResponse
    """

    db_models = _db_access.get(
        _db_models.CarActionStateDBModel,
        criteria={"timestamp": lambda x: x >= since, "car_id": lambda x: x == car_id},
        sort_result_by={"timestamp": "desc", "id": "desc"},
        first_n=last_n,
        wait=wait,
    )
    states = [
        _obj_to_db.car_action_state_from_db_model(car_state_db_model)
        for car_state_db_model in db_models
    ]
    states.sort(key=lambda x: x.timestamp)
    return _json_response(states)


def pause_car(car_id: int) -> _Response:
    """Finds and pauses a Car with given carId, if not already paused. Sets car action status to PAUSED if it is not in PAUSED action status already.

     # noqa: E501

    :param car_id: ID of the Car which should be paused.
    :type car_id: int

    :rtype: ConnexionResponse
    """

    state = CarActionState(car_id=car_id, action_status="paused")
    return create_car_action_states_from_argument_and_save_to_db([state])


def unpause_car(car_id):  # noqa: E501
    """Finds and unpauses a Car with given carId, if paused. Sets car action status to NORMAL only if it is in PAUSED action status.

     # noqa: E501

    :param car_id: ID of the Car which should be unpaused.
    :type car_id: int

    :rtype: ConnexionResponse
    """
    return "do some magic!"


def create_car_action_states_from_argument_and_save_to_db(
    states: list[CarActionState],
) -> _Response:
    """Post new car action states using list passed as argument.

    If some of the car action states' creation fails, no states are added to the server.

    The car action state creation can succeed only if:
    - the car exists.
    """
    if not states:
        return _json_response([])
    state_db_models = [_obj_to_db.car_action_state_to_db_model(s) for s in states]
    response = _db_access.add(
        *state_db_models,
        checked=[_db_access.db_object_check(_db_models.CarDBModel, id_=states[0].car_id)],
    )
    title = ""
    if response.status_code == 200:
        inserted_models = [_obj_to_db.car_action_state_from_db_model(s) for s in response.body]
        for model in inserted_models:
            code, msg = 200, f"Car action state (ID={model.id}) was succesfully created."
            _log_info(msg)
        return _json_response(inserted_models)
    else:
        code, msg, title = (
            response.status_code,
            f"Car action state could not be created. {response.body['detail']}",
            response.body["title"],
        )
        _log_error(msg)
    return _error(code=code, msg=msg, title=title)
