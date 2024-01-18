import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models.order import Order
from fleet_management_api.api_impl.db_models import OrderDBModel, CarDBModel, order_to_db_model
import fleet_management_api.database.db_access as db_access
from fleet_management_api.api_impl.api_logging import log_error, log_info


def create_order(order):
    if not connexion.request.is_json:
        code, msg = 400, f"Invalid request format: {connexion.request.data}. JSON is required"
        log_error(msg)
        return ConnexionResponse(status_code=code, content_type="text/plain", body=msg)

    order = Order.from_dict(connexion.request.get_json())
    if _car_exist(order.car_id):
        db_model = order_to_db_model(order)
        response = db_access.add_record(OrderDBModel, db_model)
        if response.status_code == 200:
            code, msg = 200, f"Order (id={order.id}) has been created and sent."
            log_info(msg)
        else:
            code, msg = response.status_code, "Error when sending order: {response.body}."
            log_error(msg)
    else:
        code, msg = 404, f"Car with id={order.car_id} does not exist"
        log_error(msg)

    return ConnexionResponse(status_code=code, content_type="text/plain", body=msg)


def _car_exist(car_id: int) -> bool:
    return bool(db_access.get_records(CarDBModel, equal_to={'id': car_id}))