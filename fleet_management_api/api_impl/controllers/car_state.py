from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    text_response as _text_response,
    error as _error,
)
from fleet_management_api.api_impl.api_logging import (
    log_info as _log_info,
    log_info_and_respond as _log_info_and_respond,
    log_error as _log_error,
    log_warning_or_error_and_respond as _log_warning_or_error_and_respond,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
from fleet_management_api.models import CarState as _CarState
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.api_impl.obj_to_db as _obj_to_db
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.api_impl.tenants import AccessibleTenants as _AccessibleTenants
from fleet_management_api.api_impl.controller_decorators import (
    with_processed_request as _with_processed_request,
    ProcessedRequest as _ProcessedRequest,
)


@_with_processed_request(require_data=True)
def create_car_states(request: _ProcessedRequest, **kwargs) -> _Response:
    """Post new car states.

    If some of the car states' creation fails, no car states are added to the server.

    The car state creation can succeed only if:
    - the car exists.
    """
    car_states = [_CarState.from_dict(s) for s in request.data]  # noqa: E501
    return create_car_states_from_argument_and_post(request.tenants, car_states)


def create_car_states_from_argument_and_post(
    tenants: _AccessibleTenants, car_states: list[_CarState]
) -> _Response:
    """Post new car states using list passed as argument.

    If some of the car states' creation fails, no car states are added to the server.

    The car state creation can succeed only if:
    - the car exists.
    """
    if not car_states:
        return _json_response([])
    state_db_models = [_obj_to_db.car_state_to_db_model(s) for s in car_states]
    response = _db_access.add(
        tenants,
        *state_db_models,
        checked=[_db_access.db_object_check(_db_models.CarDB, id_=car_states[0].car_id)],
    )
    if response.status_code == 200:
        inserted_models = [_obj_to_db.car_state_from_db_model(s) for s in response.body]
        for model in inserted_models:
            code, msg = 200, f"Car state (ID={model.id}) was succesfully created."
            _log_info(msg)
            cleanup_response = _remove_old_states(tenants, model.car_id)
        if cleanup_response.status_code != 200:
            code, cleanup_error_msg = (
                cleanup_response.status_code,
                cleanup_response.body,
            )
            _log_error(cleanup_error_msg)
            msg = msg + "\n" + cleanup_error_msg
            title = "Could not delete object"
        else:
            return _json_response(inserted_models)
    else:
        code, msg, title = (
            response.status_code,
            f"Car state could not be created. {response.body['detail']}",
            response.body["title"],
        )
        _log_error(msg)
    return _error(code=code, msg=msg, title=title)


@_with_processed_request
def get_all_car_states(
    request: _ProcessedRequest, since: int = 0, wait: bool = False, last_n: int = 0, **kwargs
) -> _Response:
    """Get all car states for all the cars.

    :param since: Only states with timestamp greater or equal to 'since' will be returned. If 'wait' is True
        and there are no states with timestamp greater or equal to 'since', the request will wait for new states.
        Default value is 0.

    :param wait: If True, wait for new states if there are no states yet.
    :param last_n: If greater than 0, return only up to 'last_n' states with highest timestamp.
    """
    # first, return car_states with highest timestamp sorted by timestamp and id in descending order
    car_state_db_models = _db_access.get(
        request.tenants,
        _db_models.CarStateDB,
        criteria={"timestamp": lambda x: x >= since},
        sort_result_by={"timestamp": "desc", "id": "desc"},
        first_n=last_n,
        wait=wait,
    )
    car_states = [
        _obj_to_db.car_state_from_db_model(car_state_db_model)
        for car_state_db_model in car_state_db_models
    ]
    car_states.sort(key=lambda x: x.timestamp)
    return _json_response(car_states)


@_with_processed_request
def get_car_states(
    request: _ProcessedRequest,
    car_id: int,
    since: int = 0,
    wait: bool = False,
    last_n: int = 0,
    **kwargs,
) -> _Response:
    """Get car states for a car idenfified by 'car_id' of an existing car.

    :param since: Only states with timestamp greater or equal to 'since' will be returned. If 'wait' is True
        and there are no states with timestamp greater or equal to 'since', the request will wait for new states.
        Default value is 0.

    :param wait: If True, wait for new states if there are no states yet.
    :param last_n: If greater than 0, return only up to 'last_n' states with highest timestamp.
    """
    try:
        if not _db_access.get_by_id(_db_models.CarDB, car_id):
            raise _db_access.ParentNotFound
        car_state_db_models = _db_access.get(
            request.tenants,
            base=_db_models.CarStateDB,
            criteria={
                "car_id": lambda i: i == car_id,
                "timestamp": lambda x: x >= since,
            },
            wait=wait,
            first_n=last_n,
            sort_result_by={"timestamp": "desc", "id": "desc"},
        )
        car_states = [_obj_to_db.car_state_from_db_model(car_state_db_model) for car_state_db_model in car_state_db_models]  # type: ignore
        car_states.sort(key=lambda x: x.timestamp)
        return _json_response(car_states)
    except _db_access.ParentNotFound as e:
        return _log_info_and_respond(
            f"Car with ID={car_id} not found. {e}",
            404,
            title="Referenced object not found",
        )
    except Exception as e:  # pragma: no cover
        return _log_warning_or_error_and_respond(str(e), 500, title="Unexpected internal error")


def _remove_old_states(tenants: _AccessibleTenants, car_id: int) -> _Response:
    car_state_db_models = _db_access.get(
        tenants, _db_models.CarStateDB, criteria={"car_id": lambda x: x == car_id}
    )
    curr_n_of_states = len(car_state_db_models)
    delta = curr_n_of_states - _db_models.CarStateDB.max_n_of_stored_states()
    if delta > 0:
        response = _db_access.delete_n(
            _db_models.CarStateDB,
            delta,
            column_name="timestamp",
            start_from="minimum",
            criteria={"car_id": lambda x: x == car_id},
        )
        return response
    else:
        return _text_response("")
