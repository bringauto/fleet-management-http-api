from typing import Optional
from collections import defaultdict

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
from fleet_management_api.response_consts import OBJ_NOT_FOUND as _OBJ_NOT_FOUND
from fleet_management_api.api_impl.load_request import (
    RequestJSON as _RequestJSON,
    RequestNoData as _RequestNoData,
)
from fleet_management_api.api_impl.tenants import AccessibleTenants as _AccessibleTenants


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
            orders: list[_models.Order] = response.body
            _active_orders[car_id] = [
                order.id
                for order in orders
                if order.last_state is not None and order.last_state.status not in FINAL_STATUSES
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
            orders: list[_models.Order] = response.body
            _inactive_orders[car_id] = [
                order.id
                for order in orders
                if order.last_state is not None and order.last_state.status in FINAL_STATUSES
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
    """Remove an order from both active and inactive orders."""
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


def create_orders() -> _Response:
    """Post new orders.

    If some of the orders' creation fails, no orders are added to the server.

    The order creation can succeed only if:
    - the car exists,
    - the target stop exists,
    - the route exists and contains the target stop,
    - the maximum number of active orders for any referenced car has not been reached.
    """
    request = _RequestJSON.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    order_db_models: list[_db_models.OrderDB] = []
    checked: list[_db_access.CheckBeforeAdd] = []
    if not isinstance(request.data, list):
        return _error(400, "Invalid input: expected a list of orders.", "Bad Request")

    orders: list[_models.Order] = [_models.Order.from_dict(o) for o in request.data]
    orders_per_car = _group_new_orders_by_car(orders)

    if _max_n_of_active_orders is not None:
        for car_id in orders_per_car:
            if len(orders_per_car[car_id]) > _max_n_of_active_orders - n_of_active_orders(car_id):
                return _error(
                    403,
                    f"Maximum number {_max_n_of_active_orders} of active orders has been reached.",
                    "Too many orders",
                )

    for order in orders:
        order.last_state = None  # type: ignore
        car_id = order.car_id
        if not _car_exist(tenants, car_id):
            return _log_error_and_respond(
                f"Car with ID={car_id} does not exist.", 404, _OBJ_NOT_FOUND
            )
        checked.extend(
            [
                _db_access.db_object_check(_db_models.CarDB, id_=order.car_id),
                _db_access.db_object_check(_db_models.StopDB, id_=order.target_stop_id),
                _db_access.db_object_check(
                    _db_models.RouteDB,
                    order.stop_route_id,
                    _db_access.db_obj_condition(
                        attribute_name="stop_ids",
                        func=lambda x: order.target_stop_id in x,
                        fail_message=f"Route with ID={order.stop_route_id} does not contain "
                        f"stop with ID={order.target_stop_id}",
                    ),
                ),
            ]
        )
        order_db_models.append(_obj_to_db.order_to_db_model(order))

    response = _db_access.add(tenants, *order_db_models, checked=checked)

    if response.status_code == 200:
        # orders are created in the database, now log them
        posted_db_models: list[_db_models.OrderDB] = response.body
        ids: list[int] = []
        for model in posted_db_models:
            assert model.id is not None
            ids.append(model.id)
            _log_info(f"Order (ID={model.id}) has been created.")

        db_states = _post_default_order_states(tenants, ids).body
        states = [_obj_to_db.order_state_from_db_model(db_state) for db_state in db_states]

        posted_orders: list[_models.Order] = []
        for model, state in zip(posted_db_models, states):
            posted_order = _obj_to_db.order_from_db_model(model, state)
            _add_active_order(order.car_id, posted_order.id)
            posted_orders.append(posted_order)

        return _json_response(posted_orders)
    else:
        return _log_error_and_respond(
            f"Error when sending order. {response.body['detail']}.",
            response.status_code,
            response.body["title"],
        )


def delete_order(car_id: int, order_id: int) -> _Response:
    """Delete an existing order."""
    request = _RequestNoData.load()
    if not request:
        return _log_invalid_request_body_format()
    tenant = _AccessibleTenants(request)
    response = _db_access.delete(tenant, _db_models.OrderDB, order_id)
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
    request = _RequestNoData.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    order_db_models = _db_access.get(
        tenants,
        base=_db_models.OrderDB,
        criteria={"id": lambda x: x == order_id, "car_id": lambda x: x == car_id},
    )
    if len(order_db_models) == 0:
        msg = f"Order with ID={order_id} assigned to car with ID={car_id} was not found."
        _log_error(msg)
        return _error(404, msg, _OBJ_NOT_FOUND)
    else:
        db_order = order_db_models[0]
        order = _get_order_with_last_state(tenants, db_order)
        _log_info(f"Found order with ID={order_id} of car with ID={car_id}.")
        return _json_response(order)  # type: ignore


def get_car_orders(car_id: int, since: int = 0) -> _Response:
    """Get all orders for a given car."""

    request = _RequestNoData.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    if not _car_exist(tenants, car_id):
        return _log_error_and_respond(
            f"Car with ID={car_id} does not exist.", 404, title=_OBJ_NOT_FOUND
        )

    db_orders: list[_db_models.OrderDB] = _db_access.get_children(  # type: ignore
        parent_base=_db_models.CarDB,
        parent_id=car_id,
        children_col_name="orders",
        criteria={"timestamp": lambda z: z >= since},
    )
    orders: list[_models.Order] = list()
    for db_order in db_orders:
        order = _get_order_with_last_state(tenants, db_order)
        if order is not None:
            orders.append(order)
    _log_info(f"Returning {len(orders)} orders for car with ID={car_id}.")
    return _json_response(orders)


def get_orders(since: int = 0) -> _Response:
    """Get all existing orders."""
    request = _RequestNoData.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    _log_info("Listing all existing orders.")
    db_orders = _db_access.get(
        tenants, _db_models.OrderDB, criteria={"timestamp": lambda x: x >= since}
    )
    orders: list[_models.Order] = list()
    for db_order in db_orders:
        order = _get_order_with_last_state(tenants, db_order)
        if order is not None:
            orders.append(order)
    return _json_response(orders)


def _car_exist(tenants: _AccessibleTenants, car_id: int) -> bool:
    return bool(_db_access.exists(tenants, _db_models.CarDB, {"id": lambda x: x == car_id}))


def _get_order_with_last_state(
    tenants: _AccessibleTenants,
    order_db_model: _db_models.OrderDB,
) -> _models.Order | None:
    last_state = _get_last_order_state(tenants, order_db_model)
    order = _obj_to_db.order_from_db_model(order_db_model=order_db_model, last_state=last_state)
    return order


def _group_new_orders_by_car(
    orders: list[_models.Order],
) -> dict[CarId, list[_models.Order]]:
    orders_by_car: dict[CarId, list[_models.Order]] = defaultdict(list)
    for order in orders:
        orders_by_car[order.car_id].append(order)
    return orders_by_car


def _get_last_order_state(
    tenants: _AccessibleTenants, order_model_db: _db_models.OrderDB
) -> _models.OrderState | None:
    db_last_states = _db_access.get(
        tenants,
        _db_models.OrderStateDB,
        criteria={"order_id": lambda x: x == order_model_db.id},
        sort_result_by={"timestamp": "desc", "id": "desc"},
        first_n=1,
    )
    if db_last_states:
        return _obj_to_db.order_state_from_db_model(db_last_states[0])
    else:
        return None


def _default_order_state(order_id: int) -> _models.OrderState:
    return _models.OrderState(order_id=order_id, status=DEFAULT_STATUS)


def _post_default_order_states(tenants: _AccessibleTenants, order_ids: list[int]) -> _Response:
    order_states = [_default_order_state(id_) for id_ in order_ids]
    response = _order_state.create_order_states_from_argument_and_post(
        tenants, order_states, check_final_state=False
    )
    return response
