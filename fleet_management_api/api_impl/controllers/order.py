from typing import Optional
from collections import defaultdict

import connexion  # type: ignore

from fleet_management_api.api_impl.api_responses import (
    error as _error,
    json_response as _json_response,
    text_response as _text_response,
    Response as _Response,
)
from fleet_management_api.api_impl.api_logging import (
    log_error as _log_error,
    log_error_and_respond as _log_error_and_respond,
    log_info as _log_info,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.api_impl.obj_to_db as _obj_to_db
import fleet_management_api.api_impl.controllers.order_state as _order_state


CarId = int
OrderId = int


_active_orders: dict[CarId, list[OrderId]] = defaultdict(list)
_inactive_orders: dict[CarId, list[OrderId]] = defaultdict(list)
_max_n_of_active_orders: Optional[int] = None
_max_n_of_inactive_orders: Optional[int] = None


DEFAULT_STATUS = _models.OrderStatus.TO_ACCEPT
FINAL_STATUSES = {_models.OrderStatus.DONE, _models.OrderStatus.CANCELED}


def clear_active_orders(car_id: Optional[CarId] = None) -> None:
    """Remove cached active order IDs. If car_id is provided, remove only orders for that car."""
    global _active_orders
    if car_id is not None and car_id in _active_orders:
        del _active_orders[car_id]
    else:
        _active_orders.clear()


def clear_inactive_orders(car_id: Optional[CarId] = None) -> None:
    """Remove cached inactive order IDs. If car_id is provided, remove only orders for that car."""
    global _inactive_orders
    if car_id is not None and car_id in _inactive_orders:
        del _inactive_orders[car_id]
    else:
        _inactive_orders.clear()


def n_of_active_orders(car_id: int) -> int:
    """Return the current number of active orders for a given car."""
    global _active_orders
    if car_id not in _active_orders:
        response = get_car_orders(car_id)
        if response.status_code != 200:
            _active_orders[car_id] = list()
        else:
            _active_orders[car_id] = [
                order.id for order in response.body if order.last_state.status not in FINAL_STATUSES
            ]
    return len(_active_orders[car_id])


def n_of_inactive_orders(car_id: int) -> int:
    """Return the current number of inactive orders for a given car."""
    global _inactive_orders
    if car_id not in _inactive_orders:
        response = get_car_orders(car_id)
        if response.status_code != 200:
            _inactive_orders[car_id] = list()
        else:
            _inactive_orders[car_id] = [
                order.id for order in response.body if order.last_state.status in FINAL_STATUSES
            ]
    return len(_inactive_orders[car_id])


def max_n_of_active_orders() -> int | None:
    """Return the maximum number of active orders that can be assigned to any car."""
    global _max_n_of_active_orders
    return _max_n_of_active_orders


def max_n_of_inactive_orders() -> int | None:
    """Return the maximum number of inactive orders that can be assigned to any car."""
    global _max_n_of_inactive_orders
    return _max_n_of_inactive_orders


def set_max_n_of_active_orders(n: None | int) -> None:
    """Set the maximum number of active orders that can be assigned to any car."""
    global _max_n_of_active_orders
    _max_n_of_active_orders = n


def set_max_n_of_inactive_orders(n: None | int) -> None:
    """Set the maximum number of inactive orders that can be assigned to any car."""
    global _max_n_of_inactive_orders
    _max_n_of_inactive_orders = n


def _remove_active_order(car_id: CarId, order_id: OrderId) -> None:
    global _active_orders
    if order_id in _active_orders[car_id]:
        _active_orders[car_id].remove(order_id)


def from_active_to_inactive_order(order_id: OrderId) -> int | None:
    """Move an order from active to inactive orders.  Return the car ID if the order was found, None otherwise."""
    global _active_orders, _inactive_orders
    for car_id in _active_orders:
        if order_id in _active_orders[car_id]:
            _active_orders[car_id].remove(order_id)
            add_inactive_order(car_id, order_id)
            return car_id
    return None


def remove_order(car_id: CarId, order_id: OrderId) -> None:
    """Remove an order from both active or inactive orders."""
    _remove_active_order(car_id, order_id)
    _remove_inactive_order(car_id, order_id)


def _remove_inactive_order(car_id: CarId, order_id: OrderId) -> None:
    global _inactive_orders
    if car_id in _inactive_orders and order_id in _inactive_orders[car_id]:
        _inactive_orders[car_id].remove(order_id)


def _add_active_order(car_id: CarId, order_id: OrderId) -> None:
    """Add an order to the list of active orders."""
    global _active_orders
    if car_id in _active_orders and order_id in _active_orders[car_id]:
        return
    _active_orders[car_id].append(order_id)


def add_inactive_order(car_id: CarId, order_id: OrderId) -> None:
    """Add an order to the list of inactive orders."""
    global _inactive_orders
    if car_id in _inactive_orders and order_id not in _inactive_orders[car_id]:
        _inactive_orders[car_id].append(order_id)


def create_order() -> _Response:
    """Post a new order. The order must have a unique id and the car must exist."""
    if not connexion.request.is_json:
        return _log_invalid_request_body_format()

    order_dict = connexion.request.get_json()
    order_dict["lastState"] = None
    order = _models.Order.from_dict(order_dict)
    car_id = order.car_id
    if not _car_exist(car_id):
        return _log_error_and_respond(
            f"Car with ID={car_id} does not exist.", 404, "Object not found"
        )
    if _max_n_of_active_orders is not None:
        car_id = order.car_id
        if n_of_active_orders(car_id) >= _max_n_of_active_orders:
            return _error(
                403,
                f"Maximum number {max_n_of_active_orders()} of active orders has been reached.",
                "Too many orders",
            )

    db_model = _obj_to_db.order_to_db_model(order)
    response = _db_access.add(
        db_model,
        checked=[
            _db_access.db_object_check(_db_models.CarDBModel, id_=order.car_id),
            _db_access.db_object_check(_db_models.StopDBModel, id_=order.target_stop_id),
            _db_access.db_object_check(
                _db_models.RouteDBModel,
                order.stop_route_id,
                _db_access.db_obj_condition(
                    attribute_name="stop_ids",
                    func=lambda x: order.target_stop_id in x,
                    fail_message=f"Route with ID={order.stop_route_id} does not contain "
                    f"stop with ID={order.target_stop_id}",
                ),
            ),
        ],
    )
    if response.status_code == 200:
        posted_db_model: _db_models.OrderDBModel = response.body[0]
        assert posted_db_model.id is not None
        db_state = _post_default_order_state(posted_db_model.id).body
        state = _obj_to_db.order_state_from_db_model(db_state)
        posted_order = _obj_to_db.order_from_db_model(posted_db_model, state)
        _log_info(f"Order (ID={posted_order.id}) has been created.")
        _add_active_order(order.car_id, posted_order.id)
        return _json_response(posted_order)
    else:
        return _log_error_and_respond(
            f"Error when sending order. {response.body['detail']}.",
            response.status_code,
            response.body["title"],
        )


def delete_order(car_id: int, order_id: int) -> _Response:
    """Delete an existing order."""
    response = _db_access.delete(_db_models.OrderDBModel, order_id)
    if response.status_code == 200:
        msg = f"Order (ID={order_id}) has been deleted."
        _log_info(msg)
        remove_order(car_id, order_id=order_id)
        return _text_response(f"Order (ID={order_id})has been succesfully deleted.")
    else:
        msg = f"Order (ID={order_id}) could not be deleted. {response.body['detail']}"
        _log_error(msg)
        return _error(response.status_code, msg, response.body["title"])


def delete_oldest_inactive_order(car_id: int) -> _Response:
    """Delete n oldest inactive orders."""
    oldest_inactive_order_id = _inactive_orders[car_id].pop(0)
    delete_order(car_id, oldest_inactive_order_id)


def get_order(car_id: int, order_id: int) -> _Response:
    """Get an existing order."""
    order_db_models = _db_access.get(
        base=_db_models.OrderDBModel,
        criteria={"id": lambda x: x == order_id, "car_id": lambda x: x == car_id},
    )
    if len(order_db_models) == 0:
        msg = f"Order with ID={order_id} assigned to car with ID={car_id} was not found."
        _log_error(msg)
        return _error(404, msg, "Object not found")
    else:
        db_order = order_db_models[0]
        order = _get_order_with_last_state(db_order)
        _log_info(f"Found order with ID={order_id} of car with ID={car_id}.")
        return _json_response(order)  # type: ignore


def get_car_orders(car_id: int, since: int = 0) -> _Response:
    """Get all orders for a given car."""
    if not _car_exist(car_id):
        return _log_error_and_respond(
            f"Car with ID={car_id} does not exist.", 404, title="Object not found"
        )
    db_orders: list[_db_models.OrderDBModel] = _db_access.get_children(  # type: ignore
        parent_base=_db_models.CarDBModel,
        parent_id=car_id,
        children_col_name="orders",
        criteria={"timestamp": lambda z: z >= since},
    )
    orders: list[_models.Order] = list()
    for db_order in db_orders:
        order = _get_order_with_last_state(db_order)
        orders.append(order)
    _log_info(f"Returning {len(orders)} orders for car with ID={car_id}.")
    return _json_response(orders)


def get_orders(since: int = 0) -> _Response:
    """Get all existing orders."""
    _log_info("Listing all existing orders.")
    db_orders = _db_access.get(
        _db_models.OrderDBModel, criteria={"timestamp": lambda x: x >= since}
    )
    orders: list[_models.Order] = list()
    for db_order in db_orders:
        order = _get_order_with_last_state(db_order)
        orders.append(order)
    return _json_response(orders)


def _get_order_with_last_state(order_db_model: _db_models.OrderDBModel) -> _models.Order:
    db_last_state = _db_access.get(
        _db_models.OrderStateDBModel,
        criteria={"order_id": lambda x: x == order_db_model.id},
        sort_result_by={"timestamp": "desc", "id": "desc"},
        first_n=1,
    )
    last_state = _obj_to_db.order_state_from_db_model(db_last_state[0])
    order = _obj_to_db.order_from_db_model(order_db_model, last_state)
    return order


def _car_exist(car_id: int) -> bool:
    return bool(_db_access.get(_db_models.CarDBModel, criteria={"id": lambda x: x == car_id}))


def _post_default_order_state(order_id: int) -> _Response:
    order_state = _models.OrderState(order_id=order_id, status=DEFAULT_STATUS)
    response = _order_state.create_order_state_from_argument_and_post(order_state)
    return response
