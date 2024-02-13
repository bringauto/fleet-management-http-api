from typing import List

import connexion  # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access


def create_order() -> _Response:
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
            check_reference_existence={
                _db_models.CarDBModel: order.car_id,
                _db_models.StopDBModel: order.target_stop_id,
                _db_models.RouteDBModel: order.stop_route_id,
            },
        )
        if response.status_code == 200:
            inserted_model = _api.order_from_db_model(response.body)
            _api.log_info(f"Order (ID={inserted_model.id}) has been created and sent.")
            return _Response(body=inserted_model, status_code=200, content_type="application/json")
        else:
            return _api.log_and_respond(
                response.status_code, f"Error when sending order. {response.body}."
            )


def delete_order(order_id: int) -> _Response:
    """Delete an existing order."""
    response = _db_access.delete(_db_models.OrderDBModel, order_id)
    if response.status_code == 200:
        msg = f"Order (ID={order_id}) has been deleted."
        _api.log_info(msg)
        return _Response(body=f"Order (ID={order_id})has been succesfully deleted.", status_code=200)
    else:
        msg = f"Order (ID={order_id}) could not be deleted. {response.body}"
        _api.log_error(msg)
        return _Response(body=msg, status_code=response.status_code)


def get_order(order_id: int) -> _Response:
    """Get an existing order."""
    order_db_models = _db_access.get(
        _db_models.OrderDBModel, criteria={"id": lambda x: x == order_id}
    )
    if len(order_db_models) == 0:
        msg = f"Order with ID={order_id} was not found."
        _api.log_error(msg)
        return _Response(body=msg, status_code=404)
    else:
        msg = f"Found order with ID={order_id}"
        _api.log_info(msg)
        return _Response(body=_api.order_from_db_model(order_db_models[0]), status_code=200)


def get_updated_orders(car_id: int) -> _Response:
    """Returns all orders for a given car that have been updated since their were last requested.

    After the order have been returned from the API, they are not longer considered updated.
    """
    if not _car_exist(car_id):
        return _api.log_and_respond(404, f"Car with ID={car_id} does not exist.")
    order_db_models: List[_db_models.OrderDBModel] = _db_access.get(
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
    return _Response(body=orders, status_code=200)


def get_orders() -> _Response:
    """Get all existing orders."""
    _api.log_info("Listing all existing orders.")
    return _Response(
        content_type="application/json",
        body=[
            _api.order_from_db_model(order_db_model)
            for order_db_model in _db_access.get(_db_models.OrderDBModel)
        ],
        status_code=200,
    )


def _car_exist(car_id: int) -> bool:
    return bool(_db_access.get(_db_models.CarDBModel, criteria={"id": lambda x: x == car_id}))
