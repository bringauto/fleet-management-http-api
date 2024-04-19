from typing import Optional
from collections import defaultdict

import connexion  # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.api_impl.controllers.order_state as _order_state


CarId = int
OrderId = int


_active_orders: dict[CarId, list[OrderId]] = defaultdict(list)
_inactive_orders: dict[CarId, list[OrderId]] = defaultdict(list)
_max_n_of_active_orders: Optional[int] = None
_max_n_of_inactive_orders: Optional[int] = None


FINAL_STATUSES = {_models.OrderStatus.DONE, _models.OrderStatus.CANCELED}



def clear_active_orders(car_id: Optional[CarId] = None) -> None:
    global _active_orders
    if car_id is not None and car_id in _active_orders:
        del _active_orders[car_id]
    else:
        _active_orders.clear()


def clear_inactive_orders(car_id: Optional[CarId] = None) -> None:
    global _inactive_orders
    if car_id is not None and car_id in _inactive_orders:
        del _inactive_orders[car_id]
    else:
        _inactive_orders.clear()


def n_of_active_orders(car_id: int) -> int:
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
    global _max_n_of_active_orders
    return _max_n_of_active_orders


def max_n_of_inactive_orders() -> int | None:
    global _max_n_of_inactive_orders
    return _max_n_of_inactive_orders


def set_max_n_of_active_orders(n: None | int) -> None:
    global _max_n_of_active_orders
    _max_n_of_active_orders = n


def set_max_n_of_inactive_orders(n: None | int) -> None:
    global _max_n_of_inactive_orders
    _max_n_of_inactive_orders = n


def _remove_active_order(car_id: CarId, order_id: OrderId) -> None:
    global _active_orders
    if order_id in _active_orders[car_id]:
        _active_orders[car_id].remove(order_id)


def from_active_to_inactive_order(order_id: OrderId) -> int | None:
    global _active_orders, _inactive_orders
    for car_id in _active_orders:
        if order_id in _active_orders[car_id]:
            _active_orders[car_id].remove(order_id)
            add_inactive_order(car_id, order_id)
            return car_id
    return None


def remove_order(car_id: CarId, order_id: OrderId) -> None:
    _remove_active_order(car_id, order_id)
    _remove_inactive_order(car_id, order_id)


def _remove_inactive_order(car_id: CarId, order_id: OrderId) -> None:
    global _inactive_orders
    if car_id in _inactive_orders and order_id in _inactive_orders[car_id]:
        _inactive_orders[car_id].remove(order_id)


def _add_active_order(car_id: CarId, order_id: OrderId) -> None:
    global _active_orders
    if car_id in _active_orders and order_id in _active_orders[car_id]:
        return
    _active_orders[car_id].append(order_id)


def add_inactive_order(car_id: CarId, order_id: OrderId) -> None:
    global _inactive_orders
    if car_id in _inactive_orders and order_id not in _inactive_orders[car_id]:
        _inactive_orders[car_id].append(order_id)


def create_order() -> _api.Response:
    """Post a new order. The order must have a unique id and the car must exist."""
    if not connexion.request.is_json:
        return _api.log_invalid_request_body_format()

    order = _models.Order.from_dict(connexion.request.get_json())
    car_id = order.car_id
    if not _car_exist(car_id):
        return _api.log_error_and_respond(
            f"Car with ID={car_id} does not exist.", 404, "Object not found"
        )
    if _max_n_of_active_orders is not None:
        car_id = order.car_id
        if n_of_active_orders(car_id) >= _max_n_of_active_orders:
            return _api.error(
                403,
                f"Maximum number {_db_models.OrderDBModel.max_n_of_active_orders()} of active orders has been reached.",
                "Too many orders",
            )

    db_model = _api.order_to_db_model(order)
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
        inserted_model = _api.order_from_db_model(response.body[0])
        _api.log_info(f"Order (ID={inserted_model.id}) has been created.")
        order_state = _models.OrderState(
            status=_models.OrderStatus.TO_ACCEPT, order_id=inserted_model.id
        )
        _order_state.create_order_state_from_argument(order_state)
        _add_active_order(car_id, inserted_model.id)
        return _api.json_response(inserted_model)
    else:
        return _api.log_error_and_respond(
            f"Error when sending order. {response.body['detail']}.",
            response.status_code,
            response.body["title"],
        )


def delete_order(car_id: int, order_id: int) -> _api.Response:
    """Delete an existing order."""
    response = _db_access.delete(_db_models.OrderDBModel, order_id)
    if response.status_code == 200:
        msg = f"Order (ID={order_id}) has been deleted."
        _api.log_info(msg)
        remove_order(car_id, order_id=order_id)
        return _api.text_response(f"Order (ID={order_id})has been succesfully deleted.")
    else:
        msg = f"Order (ID={order_id}) could not be deleted. {response.body['detail']}"
        _api.log_error(msg)
        return _api.error(response.status_code, msg, response.body["title"])


def delete_oldest_inactive_order(car_id: int) -> _api.Response:
    """Delete n oldest inactive orders."""
    oldest_inactive_order_id = _inactive_orders[car_id].pop(0)
    delete_order(car_id, oldest_inactive_order_id)


def get_order(car_id: int, order_id: int, since: int = 0) -> _api.Response:
    """Get an existing order."""
    order_db_models = _db_access.get_children(
        parent_base=_db_models.CarDBModel,
        parent_id=car_id,
        children_col_name="orders",
        criteria={"id": lambda x: x == order_id, "timestamp": lambda z: z >= since},
    )
    if len(order_db_models) == 0:
        msg = f"Order with ID={order_id} assigned to car with ID={car_id} was not found."
        _api.log_error(msg)
        return _api.error(404, msg, "Object not found")
    else:
        last_state = _db_access.get(
            _db_models.OrderStateDBModel,
            criteria={"order_id": lambda x: x == order_id},
            sort_result_by={"timestamp": "desc", "id": "desc"},
            first_n=1,
        )[0]
        msg = f"Found order with ID={order_id} of car with ID={car_id}."
        _api.log_info(msg)
        order = _api.order_from_db_model(order_db_models[0])  # type: ignore
        order.last_state = _api.order_state_from_db_model(last_state)
        return _api.json_response(order)  # type: ignore


def get_car_orders(car_id: int, since: int = 0) -> _api.Response:
    """Get all orders for a given car."""
    if not _car_exist(car_id):
        return _api.log_error_and_respond(
            f"Car with ID={car_id} does not exist.", 404, title="Object not found"
        )
    order_db_models = _db_access.get_children(
        parent_base=_db_models.CarDBModel,
        parent_id=car_id,
        children_col_name="orders",
        criteria={"timestamp": lambda z: z >= since},
    )
    orders = [_api.order_from_db_model(order_db_model) for order_db_model in order_db_models]  # type: ignore
    for order in orders:
        last_state = _db_access.get(
            _db_models.OrderStateDBModel,
            criteria={"order_id": lambda x: x == order.id},
            sort_result_by={"timestamp": "desc", "id": "desc"},
            first_n=1,
        )[0]
        order.last_state = _api.order_state_from_db_model(last_state)
    _api.log_info(f"Returning {len(orders)} orders for car with ID={car_id}.")
    return _api.json_response(orders)


def get_orders(since: int = 0) -> _api.Response:
    """Get all existing orders."""
    _api.log_info("Listing all existing orders.")
    db_orders = _db_access.get(
        _db_models.OrderDBModel, criteria={"timestamp": lambda x: x >= since}
    )
    orders = [_api.order_from_db_model(order) for order in db_orders]
    for order in orders:
        last_state = _db_access.get(
            _db_models.OrderStateDBModel,
            criteria={"order_id": lambda x: x == order.id},
            sort_result_by={"timestamp": "desc", "id": "desc"},
            first_n=1,
        )[0]
        order.last_state = _api.order_state_from_db_model(last_state)

    return _api.json_response(orders)


def _car_exist(car_id: int) -> bool:
    return bool(_db_access.get(_db_models.CarDBModel, criteria={"id": lambda x: x == car_id}))
