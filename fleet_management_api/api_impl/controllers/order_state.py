from typing import Callable, Any, Optional

import connexion as _connexion  # type: ignore

from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    text_response as _text_response,
)
from fleet_management_api.api_impl.api_logging import (
    log_info as _log_info,
    log_info_and_respond as _log_info_and_respond,
    log_error as _log_error,
    log_error_and_respond as _log_error_and_respond,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
import fleet_management_api.models as _models
import fleet_management_api.api_impl.obj_to_db as _obj_to_db
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.api_impl.controllers.order as _order


OrderId = int


_last_order_status: dict[OrderId, str] = dict()


def initialize_last_order_status_dict() -> None:
    """Initialize the dictionary that stores the last status of each order.

    The states are primarily stored in the database. The dictionary serves as a cache.
    If last status is not found in the dictionary when needed, the database is queried.

    This initialization thus does not affect recognizing the order as done or canceled.
    """
    global _last_order_status
    _last_order_status = dict()


def create_order_states() -> _Response:
    """Post new states of existing orders.

    If some of the order states's creation fails, no states are added to the server.

    Order State creation can succeed only if:
    - the order exists,
    - there is no Order State with final status (DONE or CANCELED) for the order.
    """
    if not _connexion.request.is_json:
        return _log_invalid_request_body_format()
    order_states = [_models.OrderState.from_dict(item) for item in _connexion.request.get_json()]
    return create_order_states_from_argument_and_post(order_states)


def create_order_states_from_argument_and_post(order_states: list[_models.OrderState]) -> _Response:
    """Create new states of  existing orders. The Order State models are passed as an argument.

    Order State creation can succeed only if:
    - the order exists,
    - there is no Order State with final status (DONE or CANCELED) for the order.
    """
    order_ids = [order_state.order_id for order_state in order_states]
    orders: dict[int, _db_models.OrderDBModel | None] = _existing_orders(*order_ids)
    for id_, order in orders.items():
        if order is None:
            return _log_error_and_respond(
                f"Order with id='{id_}' was not found.", 404, "Object not found"
            )

    # order exists
    for state in order_states:
        if _is_order_done(state):
            return _log_error_and_respond(
                f"Order with id='{state.order_id}' has already received status DONE."
                "No other Order State can be added.",
                403,
                title="Could not create new object",
            )
        elif _is_order_canceled(state):
            return _log_error_and_respond(
                f"Order with id='{state.order_id}' has already received status CANCELED."
                "No other Order State can be added.",
                403,
                title="Could not create new object",
            )

    db_models: list[_db_models.OrderStateDBModel] = []

    for state in order_states:
        db_model = _obj_to_db.order_state_to_db_model(state)
        order = orders[state.order_id]
        assert order is not None
        db_model.car_id = order.car_id
        db_models.append(db_model)

    response = _db_access.add(*db_models)
    if response.status_code == 200:
        inserted_models = [_obj_to_db.order_state_from_db_model(m) for m in response.body]
        for model in inserted_models:
            _remove_old_states(model.order_id)
            _log_info(f"Order state (ID={model.id}) has been sent.")
            _save_last_status(model)
            if model.status in {_models.OrderStatus.DONE, _models.OrderStatus.CANCELED}:
                car_id = _order.from_active_to_inactive_order(model.order_id)
                max_n = _order.max_n_of_inactive_orders()
                if max_n is not None and car_id is not None:
                    n_of_inactive = _order.n_of_inactive_orders(car_id)
                    if n_of_inactive > max_n:
                        _order.delete_oldest_inactive_order(car_id)
        return _json_response(inserted_models)
    else:
        return _log_error_and_respond(
            f"Order state could not be sent. {response.body['detail']}",
            response.status_code,
            title=response.body["title"],
        )


def get_all_order_states(wait: bool = False, since: int = 0, last_n: int = 0, car_id: Optional[int] = None) -> _Response:
    """Get all order states for all the existing orders.

    :param since: Only states with timestamp greater or equal to 'since' will be returned. If 'wait' is True
        and there are no states with timestamp greater or equal to 'since', the request will wait for new states.
        Default value is 0.

    :param wait: If True, wait for new states if there are no states for the order yet.
    :param last_n: If greater than 0, return only up to 'last_n' states with highest timestamp.
    :param car_id: If not None, return only states of orders that are assigned to the car with 'car_id'.
    If None, return states of all orders. If the car with the specified 'car_id' does not exist,
    return empty list.
    """
    _log_info("Getting all order states for all orders.")
    if car_id is not None:
        return _get_order_states({"car_id": lambda x: x == car_id}, wait, since, last_n)
    else:
        return _get_order_states({}, wait, since, last_n=last_n)


def get_order_states(
    order_id: int, wait: bool = False, since: int = 0, last_n: int = 0
) -> _Response:
    """Get all order states for an order identified by 'order_id' of an existing order.

    :param order_id: Id of the order.

    :param since: Only states with timestamp greater or equal to 'since' will be returned. If 'wait' is True
        and there are no states with timestamp greater or equal to 'since', the request will wait for new states.
        Default value is 0.

    :param wait: If True, wait for new states if there are no states for the order yet.
    :param last_n: If greater than 0, return only up to 'last_n' states with highest timestamp.
    """
    if _existing_orders(order_id)[order_id] is None:
        _log_error(f"Order with id='{order_id}' was not found. Cannot get its states.")
        return _json_response([], code=404)
    else:
        criteria: dict[str, Callable[[Any], bool]] = {"order_id": lambda x: x == order_id}
        return _get_order_states(criteria, wait, since, last_n)


def _get_order_states(
    criteria: dict[str, Callable[[Any], bool]], wait: bool, since: int, last_n: int = 0
) -> _Response:
    criteria["timestamp"] = lambda x: x >= since
    order_state_db_models = _db_access.get(
        _db_models.OrderStateDBModel,
        wait=wait,
        criteria=criteria,
        first_n=last_n,
        sort_result_by={"timestamp": "desc", "id": "desc"},
    )
    order_states = [
        _obj_to_db.order_state_from_db_model(order_state_db_model)
        for order_state_db_model in order_state_db_models
    ]
    order_states.sort(key=lambda x: x.timestamp)
    return _json_response(order_states)


def _remove_old_states(order_id: int) -> _Response:
    order_state_db_models = _db_access.get(
        _db_models.OrderStateDBModel, criteria={"order_id": lambda x: x == order_id}
    )
    delta = len(order_state_db_models) - _db_models.OrderStateDBModel.max_n_of_stored_states()
    if delta > 0:
        response = _db_access.delete_n(
            _db_models.OrderStateDBModel,
            n=delta,
            column_name="timestamp",
            start_from="minimum",
            criteria={"order_id": lambda x: x == order_id},
        )
        return _log_info_and_respond(response.body)
    else:
        return _text_response("No old order states to remove.")


def _existing_orders(*order_ids: int) -> dict[int, _db_models.OrderDBModel | None]:
    order_ids = tuple(dict.fromkeys(order_ids).keys())
    models: dict[int, _db_models.OrderDBModel | None] = dict()
    for id_ in order_ids:
        models_with_id = _db_access.get(
            _db_models.OrderDBModel, criteria={"id": lambda x: x == id_}
        )
        if models_with_id:
            models[id_] = models_with_id[0]
        else:
            models[id_] = None
    return models

def _is_order_done(order_state: _models.OrderState) -> bool:
    _load_last_status_from_db_if_missing(order_state)
    return _last_order_status.get(order_state.order_id) == _models.OrderStatus.DONE


def _is_order_canceled(order_state: _models.OrderState) -> bool:
    _load_last_status_from_db_if_missing(order_state)
    return _last_order_status.get(order_state.order_id) == _models.OrderStatus.CANCELED


def _save_last_status(order_state: _models.OrderState) -> None:
    _last_order_status[order_state.order_id] = str(order_state.status)


def _load_last_status_from_db_if_missing(order_state: _models.OrderState) -> None:
    if order_state.order_id not in _last_order_status:
        order_state_db_models: list[_db_models.OrderStateDBModel] = _db_access.get(
            _db_models.OrderStateDBModel,
            criteria={"order_id": lambda x: x == order_state.order_id},
            wait=False,
        )
        if order_state_db_models:
            _last_order_status[order_state.order_id] = order_state_db_models[-1].status
    return
