from typing import List, Tuple

import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models.order import Order
from fleet_management_api.api_impl.db_models import OrderDBModel, CarDBModel, order_to_db_model, order_from_db_model
import fleet_management_api.database.db_access as db_access
from fleet_management_api.api_impl.api_logging import log_error, log_info


def create_order(order) -> ConnexionResponse:
    if not connexion.request.is_json:
        return _log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")

    order = Order.from_dict(connexion.request.get_json())
    if not _car_exist(order.car_id):
        return _log_and_respond(404, f"Car with id={order.car_id} does not exist.")
    else:
        db_model = order_to_db_model(order)
        response = db_access.add_record(OrderDBModel, db_model)
        if response.status_code == 200:
            return _log_and_respond(response.status_code, f"Order (id={order.id}) has been created and sent.")
        else:
            return _log_and_respond(response.status_code, f"Error when sending order. {response.body}.")


def get_order(order_id) -> ConnexionResponse:
    orders = db_access.get_records(OrderDBModel, equal_to={'id': order_id})
    if len(orders) == 0:
        return ConnexionResponse(body=f"Order with id={order_id} was not found.", status_code=404)
    else:
        return ConnexionResponse(body=orders[0], status_code=200)


def get_orders() -> List[Order]:
    log_info("Listing all existing orders")
    return [order_from_db_model(order_db_model) for order_db_model in db_access.get_records(OrderDBModel)]


def update_order(order) -> Tuple[Order|None, int]:
    if connexion.request.is_json:
        order = Order.from_dict(connexion.request.get_json())
        order_db_model = order_to_db_model(order)
        response = db_access.update_record(id_name="id", id_value=order.id, updated_obj=order_db_model)
        if 200 <= response.status_code < 300:
            log_info(f"Order (id={order.id} has been suchas been succesfully updated.")
            return order, response.status_code
        else:
            log_error(f"Order (id={order.id}) could not be updated. {response.body}")
            return order, response.status_code
    else:
        log_error(f"Invalid request format: {connexion.request.data}. JSON is required.")
        return None, 400


def _car_exist(car_id: int) -> bool:
    return bool(db_access.get_records(CarDBModel, equal_to={'id': car_id}))


def _log_and_respond(code: int, msg: str) -> ConnexionResponse:
    if 200 <= code < 300:
        log_info(msg)
    else:
        log_error(msg)
    return ConnexionResponse(status_code=code, content_type="text/plain", body=msg)