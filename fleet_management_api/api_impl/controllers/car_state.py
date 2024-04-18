import connexion  # type: ignore


import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access


def add_car_state() -> _api.Response:
    """Post new car state.

    :param car_state: Car state to be added.

    :rtype: CarState

    The state must have a unique Id.
    The car defined by 'car_id' must exist.
    """
    if not connexion.request.is_json:
        return _api.log_invalid_request_body_format()
    else:
        car_state = _models.CarState.from_dict(connexion.request.get_json())  # noqa: E501
        return add_car_state_from_argument(car_state)


def add_car_state_from_argument(car_state: _models.CarState) -> _api.Response:
    state_db_model = _api.car_state_to_db_model(car_state)
    response = _db_access.add(
        state_db_model,
        checked=[_db_access.db_object_check(_db_models.CarDBModel, id_=car_state.car_id)],
    )
    if response.status_code == 200:
        inserted_model = _api.car_state_from_db_model(response.body[0])
        code, msg = 200, f"Car stat (ID={inserted_model.id}) was succesfully created."
        _api.log_info(msg)
        cleanup_response = _remove_old_states(car_state.car_id)
        if cleanup_response.status_code != 200:
            code, cleanup_error_msg = cleanup_response.status_code, cleanup_response.body
            _api.log_error(cleanup_error_msg)
            msg = msg + "\n" + cleanup_error_msg
            title = "Could not remove old car states."
        else:
            return _api.json_response(inserted_model)
    else:
        code, msg, title = (
            response.status_code,
            f"Car state could not be created. {response.body['detail']}",
            response.body['title']
        )
        _api.log_error(msg)
    return _api.error(code=code, msg=msg, title=title)


def get_all_car_states(since: int = 0, wait: bool = False, last_n: int = 0) -> _api.Response:
    """Get all car states for all the cars.

    :param since: Only states with timestamp greater or equal to 'since' will be returned. If 'wait' is True
        and there are no states with timestamp greater or equal to 'since', the request will wait for new states.
        Default value is 0.

    :param wait: If True, wait for new states if there are no states yet.
    :param last_n: If greater than 0, return only up to 'last_n' states with highest timestamp.
    """
    # first, return car_states with highest timestamp sorted by timestamp and id in descending order
    car_state_db_models = _db_access.get(
        _db_models.CarStateDBModel,
        criteria={"timestamp": lambda x: x >= since},
        sort_result_by={"timestamp": "desc", "id": "desc"},
        first_n=last_n,
        wait=wait
    )
    car_states = [
        _api.car_state_from_db_model(car_state_db_model)
        for car_state_db_model in car_state_db_models
    ]
    return _api.json_response(car_states)


def get_car_states(car_id: int, since: int = 0, wait: bool = False, last_n: int = 0) -> _api.Response:
    """Get car states for a car idenfified by 'car_id' of an existing car.

    :param since: Only states with timestamp greater or equal to 'since' will be returned. If 'wait' is True
        and there are no states with timestamp greater or equal to 'since', the request will wait for new states.
        Default value is 0.

    :param wait: If True, wait for new states if there are no states yet.
    :param last_n: If greater than 0, return only up to 'last_n' states with highest timestamp.
    """
    try:
        car_state_db_models = _db_access.get_children(
            parent_base=_db_models.CarDBModel,
            parent_id=car_id,
            children_col_name="states",
            criteria={"timestamp": lambda x: x >= since},
            wait=wait
        )
        car_states = [_api.car_state_from_db_model(car_state_db_model) for car_state_db_model in car_state_db_models]  # type: ignore
        return _api.json_response(car_states)
    except _db_access.ParentNotFound as e:
        return _api.log_error_and_respond(f"Car with ID={car_id} not found. {e}", 404, title="Referenced object not found")
    except Exception as e:  # pragma: no cover
        return _api.log_error_and_respond(str(e), 500, title="Unexpected internal error")


def _remove_old_states(car_id: int) -> _api.Response:
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
        return response
    else:
        return _api.text_response("")
