from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore
from fleet_management_api.models.car_action_state import (
    CarActionState,
    CarActionStatus,
)  # noqa: E501
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.api_impl.obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_responses import (
    json_response as _json_response,
    error as _error,
    text_response as _text_response,
)
from fleet_management_api.api_impl.api_logging import (
    log_info as _log_info,
    log_error as _log_error,
    log_error_and_respond as _log_error_and_respond,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
from fleet_management_api.api_impl.load_request import RequestEmpty as _RequestEmpty
from fleet_management_api.api_impl.tenants import AccessibleTenants as _AccessibleTenants


CarId = int


STATE_TRANSITIONS: dict[str, set[str]] = {
    CarActionStatus.NORMAL: {CarActionStatus.PAUSED},
    CarActionStatus.PAUSED: {CarActionStatus.NORMAL},
}


def get_car_action_states(
    car_id: int, since: int = 0, wait: bool = False, last_n: int = 0, tenant: str = ""
) -> _Response:
    """Finds car action states for a Car with given carId.

     # noqa: E501
    :rtype: ConnexionResponse
    """
    if not _db_access.get_by_id(_db_models.CarDB, car_id):
        return _log_error_and_respond(
            f"Car with ID={car_id} not found. Cannot get car action states.",
            404,
            title="Referenced object not found",
        )
    request = _RequestEmpty.load(tenant)
    if not request:
        return _log_invalid_request_body_format()
    db_models = _db_access.get(
        _AccessibleTenants(request, ""),
        _db_models.CarActionStateDB,
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


def pause_car(car_id: int, tenant: str = "") -> _Response:
    """Finds and pauses a Car with given carId, if not already paused. Sets car action status to PAUSED if it is not in PAUSED action status already.

     # noqa: E501

    :param car_id: ID of the Car which should be paused.
    :type car_id: int

    :rtype: ConnexionResponse
    """
    request = _RequestEmpty.load(tenant)
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request, "")
    state = CarActionState(car_id=car_id, action_status="paused")
    return create_car_action_states_from_argument_and_save_to_db(tenants, [state])


def unpause_car(car_id, tenant: str = ""):  # noqa: E501
    """Finds and unpauses a Car with given carId, if paused. Sets car action status to NORMAL only if it is in PAUSED action status.

     # noqa: E501

    :param car_id: ID of the Car which should be unpaused.
    :type car_id: int

    :rtype: ConnexionResponse
    """
    request = _RequestEmpty.load(tenant)
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request, "")
    state = CarActionState(car_id=car_id, action_status="normal")
    return create_car_action_states_from_argument_and_save_to_db(tenants, [state])


def create_car_action_states_from_argument_and_save_to_db(
    tenants: _AccessibleTenants,
    states: list[CarActionState],
) -> _Response:
    """Post new car action states using list passed as argument.

    If some of the car action states' creation fails, no states are added to the server.

    The car action state creation can succeed only if:
    - the car exists.

    Any two states belonging to the same car are merged,
    if they come one after another and have the same action status.
    """
    if not states:
        return _json_response([])

    last_states = get_last_action_states(tenants, *{state.car_id for state in states})
    extended_states = last_states + states
    invalid_state_transitions = check_for_invalid_car_action_state_transitions(extended_states)
    if invalid_state_transitions:
        return _error(
            400,
            f"Received invalid state transitions: {invalid_state_transitions}",
            "Consecutive states with the same action status",
        )

    state_db_models = [_obj_to_db.car_action_state_to_db_model(s) for s in states]
    response = _db_access.add(
        tenants,
        *state_db_models,
        checked=[_db_access.db_object_check(_db_models.CarDB, id_=states[0].car_id)],
    )
    title = ""
    if response.status_code == 200:
        inserted_models = [_obj_to_db.car_action_state_from_db_model(s) for s in response.body]
        invalid_cleanup_responses = []
        for model in inserted_models:
            code, msg = 200, f"Car action state (ID={model.id}) was succesfully created."
            _log_info(msg)
            cleanup_response = _remove_old_states(tenants, model.car_id)
            if cleanup_response.status_code != 200:
                invalid_cleanup_responses.append(cleanup_response)
        if invalid_cleanup_responses:
            most_severe_cleanup_response = max(
                invalid_cleanup_responses, key=lambda x: x.status_code
            )
            code, cleanup_error_msg = (
                most_severe_cleanup_response.status_code,
                most_severe_cleanup_response.body,
            )
            _log_error(cleanup_error_msg)
            msg = msg + "\n" + cleanup_error_msg
            title = "Could not delete object"
        else:
            return _json_response(inserted_models)
    else:
        code, msg, title = (
            response.status_code,
            f"Car action state could not be created. {response.body['detail']}",
            response.body["title"],
        )
        _log_error(msg)
    return _error(code=code, msg=msg, title=title)


def check_for_invalid_car_action_state_transitions(
    states: list[CarActionState],
) -> dict[CarId, list[tuple[CarActionStatus, CarActionStatus]]]:
    """Return a dictionary of car ids with invalid state transitions."""
    last_statuses: dict[CarId, CarActionStatus] = dict()
    invalid_state_transitions: dict[CarId, list[tuple[CarActionStatus, CarActionStatus]]] = dict()
    for state in states:
        car_id = state.car_id
        if car_id not in last_statuses:
            last_statuses[car_id] = state.action_status
        else:
            last_status_value = str(last_statuses[car_id])
            allowed_next_statuses = STATE_TRANSITIONS.get(last_status_value, set())
            if state.action_status not in allowed_next_statuses:
                if car_id not in invalid_state_transitions:
                    invalid_state_transitions[car_id] = []
                invalid_state_transitions[car_id].append(
                    (last_statuses[car_id], state.action_status)
                )
            last_statuses[car_id] = state.action_status
        # otherwise, the state is skipped, a.k.a. merged with the previous one
    return invalid_state_transitions


def get_last_action_states(tenants: _AccessibleTenants, *car_ids: int) -> list[CarActionState]:
    """Get last action state for each car in car_ids."""
    states = []
    for car_id in car_ids:
        db_model = _db_access.get(
            tenants,
            _db_models.CarActionStateDB,
            criteria={"car_id": lambda x: x == car_id},
            sort_result_by={"timestamp": "desc", "id": "desc"},
            first_n=1,
        )
        if db_model:
            states.append(_obj_to_db.car_action_state_from_db_model(db_model[0]))
    return states


def _remove_old_states(tenants: _AccessibleTenants, car_id: int) -> _Response:
    car_state_db_models = _db_access.get(
        tenants,
        _db_models.CarActionStateDB,
        criteria={"car_id": lambda x: x == car_id},
    )
    curr_n_of_states = len(car_state_db_models)
    delta = curr_n_of_states - _db_models.CarActionStateDB.max_n_of_stored_states()
    if delta > 0:
        response = _db_access.delete_n(
            _db_models.CarActionStateDB,
            delta,
            column_name="timestamp",
            start_from="minimum",
            criteria={"car_id": lambda x: x == car_id},
        )
        return response
    else:
        return _text_response("")
