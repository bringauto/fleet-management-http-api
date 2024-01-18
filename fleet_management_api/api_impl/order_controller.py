import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models.order import Order
from fleet_management_api.api_impl.db_models import OrderDBModel, CarDBModel, order_to_db_model, order_from_db_model
import fleet_management_api.database.db_access as db_access
from fleet_management_api.api_impl.api_logging import log_error, log_info, log_and_respond


def create_order(order) -> ConnexionResponse:
    if not connexion.request.is_json:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")

    order = Order.from_dict(connexion.request.get_json())
    if not _car_exist(order.car_id):
        return log_and_respond(404, f"Car with id={order.car_id} does not exist.")
    else:
        db_model = order_to_db_model(order)
        response = db_access.add_record(OrderDBModel, db_model)
        if response.status_code == 200:
            return log_and_respond(response.status_code, f"Order (id={order.id}) has been created and sent.")
        else:
            return log_and_respond(response.status_code, f"Error when sending order (id={order.id}). {response.body}.")


def delete_order(order_id: int) -> ConnexionResponse:
    response = db_access.delete_record(OrderDBModel, 'id', order_id)
    if 200 <= response.status_code < 300:
        msg = f"Order (id={order_id}) has been deleted."
        log_info(msg)
        return ConnexionResponse(body=f"Order (id={order_id})has been succesfully deleted", status_code=200)
    else:
        msg = f"Order (id={order_id}) could not be deleted. {response.body}"
        log_error(msg)
        return ConnexionResponse(body=msg, status_code=response.status_code)


def get_order(order_id: int) -> ConnexionResponse:
    orders = db_access.get_records(OrderDBModel, equal_to={'id': order_id})
    if len(orders) == 0:
        return ConnexionResponse(body=f"Order with id={order_id} was not found.", status_code=404)
    else:
        return ConnexionResponse(body=orders[0], status_code=200)


def get_orders() -> ConnexionResponse:
    log_info("Listing all existing orders")
    return ConnexionResponse(
        content_type="application/json",
        body=[order_from_db_model(order_db_model) for order_db_model in db_access.get_records(OrderDBModel)],
        status_code=200
    )


def update_order(order) -> ConnexionResponse:
    if connexion.request.is_json:
        order = Order.from_dict(connexion.request.get_json())
        order_db_model = order_to_db_model(order)
        response = db_access.update_record(id_name="id", id_value=order.id, updated_obj=order_db_model)
        if 200 <= response.status_code < 300:
            log_info(f"Order (id={order.id} has been suchas been succesfully updated.")
            return ConnexionResponse(status_code=200, content_type="application/json", body=order)
        elif response.status_code == 404:
            log_error(f"Order (id={order.id}) was not found and could not be updated. {response.body}")
            return ConnexionResponse(status_code=404, content_type="application/json", body=order)
        else:
            log_error(f"Order (id={order.id}) could not be updated. {response.body}")
            return ConnexionResponse(status_code=400, content_type="application/json", body=order)
    else:
        msg = f"Invalid request format: {connexion.request.data}. JSON is required."
        log_error(msg)
        return ConnexionResponse(status_code=400, content_type="text/plain", body=msg)


def _car_exist(car_id: int) -> bool:
    return bool(db_access.get_records(CarDBModel, equal_to={'id': car_id}))

