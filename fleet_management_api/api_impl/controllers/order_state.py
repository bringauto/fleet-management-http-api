from typing import Callable, Any

import connexion as _connexion  # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models


OrderId = int


FINAL_STATES = {_models.OrderStatus.DONE, _models.OrderStatus.CANCELED}


def create_order_state() -> _api.Response:
    """Post a new state of an existing order."""
    if not _connexion.request.is_json:
        return _api.log_invalid_request_body_format()
    order_state = _models.OrderState.from_dict(_connexion.request.get_json())
    return create_order_state_from_argument(order_state)


def create_order_state_from_argument(order_state: _models.OrderState) -> _api.Response:
    """Create a new state of an existing order. The Order State model is passed as an argument."""
    if not _order_exists(order_state.order_id):
        return _api.log_and_respond(404, f"Order with id='{order_state.order_id}' was not found.")
    if not _is_order_active(order_state.order_id):
        return _api.log_and_respond(
            403,
            f"Order with id='{order_state.order_id}' has already received status DONE or CANCELED. "
            "No other Order State can be added."
        )

    order_state_db_model = _api.order_state_to_db_model(order_state)
    response = _db_access.add(order_state_db_model)
    if response.status_code == 200:
        inserted_model = _api.order_state_from_db_model(response.body[0])
        _remove_old_states(order_state.order_id)
        _api.log_info(f"Order state (ID={inserted_model.id}) has been sent.")
        if inserted_model.status in FINAL_STATES:
            _remove_from_active_orders(order_state.order_id)
        return _api.json_response(200, inserted_model)
    else:
        return _api.log_and_respond(
            response.status_code, f"Order state could not be sent. {response.body}"
        )


def get_all_order_states(wait: bool = False, since: int = 0) -> _api.Response:
    """Get all order states for all the existing orders."""
    _api.log_info("Getting all order states for all orders.")
    return _get_order_states({}, wait, since)


def get_order_states(order_id: int, wait: bool = False, since: int = 0) -> _api.Response:
    """Get all order states for an order identified by 'order_id' of an existing order.

    :param order_id: Id of the order.

    :param since: Only statuses with timestamp greater or equal to 'since' will be returned. If 'wait' is True
        and there are no states with timestamp greater or equal to 'since', the request will wait for new states.
        Default value is 0.

    :param wait: If True, wait for new states if there are no states for the order yet.
    """
    if not _order_exists(order_id):
        _api.log_error(f"Order with id='{order_id}' was not found. Cannot get its states.")
        return _api.json_response(404, [])
    else:
        criteria: dict[str, Callable[[Any], bool]] = {"order_id": lambda x: x == order_id}
        return _get_order_states(criteria, wait, since)


def _get_order_states(
    criteria: dict[str, Callable[[Any], bool]], wait: bool, since: int
) -> _api.Response:
    criteria["timestamp"] = lambda x: x >= since
    order_state_db_models = _db_access.get(
        _db_models.OrderStateDBModel, wait=wait, criteria=criteria
    )
    order_states = [
        _api.order_state_from_db_model(order_state_db_model)
        for order_state_db_model in order_state_db_models
    ]
    return _api.json_response(200, order_states)


def _remove_old_states(order_id: int) -> _api.Response:
    order_state_db_models = _db_access.get(_db_models.OrderStateDBModel, criteria={"order_id": lambda x: x == order_id})
    delta = len(order_state_db_models) - _db_models.OrderStateDBModel.max_n_of_stored_states()
    if delta > 0:
        response = _db_access.delete_n(
            _db_models.OrderStateDBModel,
            n=delta,
            column_name="timestamp",
            start_from="minimum",
            criteria={"order_id": lambda x: x == order_id},
        )
        return _api.log_and_respond(response.status_code, response.body)
    else:
        return _api.text_response(200, "No old order states to remove.")


def _order_exists(order_id: int) -> bool:
    order_db_models = _db_access.get(
        _db_models.OrderDBModel, criteria={"id": lambda x: x == order_id}
    )
    return len(order_db_models) > 0


def _is_order_active(order_id: int) -> bool:
    return order_id in _db_models.OrderDBModel.active_orders


def _remove_from_active_orders(order_id: int) -> None:
    if order_id in _db_models.OrderDBModel.active_orders:
        _db_models.OrderDBModel.active_orders.remove(order_id)

