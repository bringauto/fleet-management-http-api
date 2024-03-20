import connexion  # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.api_impl.controllers.order_state import (
    create_order_state_from_argument as _create_order_state_from_argument
)


def create_order() -> _api.Response:
    """Post a new order. The order must have a unique id and the car must exist."""
    if not connexion.request.is_json:
        return _api.log_invalid_request_body_format()
    order = _models.Order.from_dict(connexion.request.get_json())
    if not _car_exist(order.car_id):
        return _api.log_and_respond(404, f"Car with ID={order.car_id} does not exist.")
    else:
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
                status=_models.OrderStatus.TO_ACCEPT,
                order_id=inserted_model.id
            )
            _create_order_state_from_argument(order_state)
            return _api.json_response(200, inserted_model)
        else:
            return _api.log_and_respond(
                response.status_code, f"Error when sending order. {response.body}."
            )


def delete_order(order_id: int) -> _api.Response:
    """Delete an existing order."""
    response = _db_access.delete(_db_models.OrderDBModel, order_id)
    if response.status_code == 200:
        msg = f"Order (ID={order_id}) has been deleted."
        _api.log_info(msg)
        return _api.text_response(200, f"Order (ID={order_id})has been succesfully deleted.")
    else:
        msg = f"Order (ID={order_id}) could not be deleted. {response.body}"
        _api.log_error(msg)
        return _api.text_response(response.status_code, msg)


def get_order(order_id: int) -> _api.Response:
    """Get an existing order."""
    order_db_models = _db_access.get(
        _db_models.OrderDBModel, criteria={"id": lambda x: x == order_id}
    )
    if len(order_db_models) == 0:
        msg = f"Order with ID={order_id} was not found."
        _api.log_error(msg)
        return _api.text_response(404, msg)
    else:
        msg = f"Found order with ID={order_id}"
        _api.log_info(msg)
        return _api.json_response(200, _api.order_from_db_model(order_db_models[0]))


def get_updated_orders(car_id: int) -> _api.Response:
    """Returns all orders for a given car that have been updated since their were last requested.

    After the order have been returned from the API, they are not longer considered updated.
    """
    if not _car_exist(car_id):
        return _api.log_and_respond(404, f"Car with ID={car_id} does not exist.")
    order_db_models: list[_db_models.OrderDBModel] = _db_access.get(
        _db_models.OrderDBModel,
        criteria={"car_id": lambda x: x == car_id, "updated": lambda x: x == True},
    )
    for m in order_db_models:
        m.updated = False
        response = _db_access.update(m)
        if response.status_code != 200:
            return _api.log_and_respond(
                response.status_code, f"Error when updating order (ID={m.id}). {response.body}"
            )
    orders = [_api.order_from_db_model(order_db_model) for order_db_model in order_db_models]
    _api.log_info(f"Returning {len(orders)} updated orders for car with ID={car_id}.")
    return _api.json_response(200, orders)


def get_orders() -> _api.Response:
    """Get all existing orders."""
    _api.log_info("Listing all existing orders.")
    body = [
        _api.order_from_db_model(order_db_model)
        for order_db_model in _db_access.get(_db_models.OrderDBModel)
    ]
    return _api.json_response(200, body)


def _car_exist(car_id: int) -> bool:
    return bool(_db_access.get(_db_models.CarDBModel, criteria={"id": lambda x: x == car_id}))
