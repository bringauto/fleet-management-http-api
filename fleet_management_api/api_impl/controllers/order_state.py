import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models.order_state import OrderState
import fleet_management_api.api_impl.obj_to_db as obj_to_db
import fleet_management_api.database.db_access as db_access
import fleet_management_api.database.db_models as db_models
from fleet_management_api.api_impl.api_logging import log_and_respond


def create_order_state(order_state) -> ConnexionResponse:
    if not connexion.request.is_json:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")

    order_state = OrderState.from_dict(connexion.request.get_json())
    order_db_model = db_access.get_records(db_models.OrderDBModel, equal_to={'id': order_state.order_id})
    if len(order_db_model) == 0:
        code, msg = 404, f"Order with id='{order_state.order_id}' was not found."
        return log_and_respond(code, msg)

    order_state_db_model = obj_to_db.order_state_to_db_model(order_state)
    response = db_access.add_record(db_models.OrderStateDBModel, order_state_db_model)
    if response.status_code == 200:
        _mark_order_as_updated(order_state.order_id)
        return log_and_respond(200, f"Order state (id={order_state.id}) has been sent.")
    elif response.status_code == 400:
        return log_and_respond(response.status_code, f"Order state (id={order_state.id}) could not be sent. {response.body}")
    else:
        return log_and_respond(response.status_code, response.body)


def get_all_order_states() -> ConnexionResponse:
    order_state_db_models = db_access.get_records(db_models.OrderStateDBModel)
    order_states = [obj_to_db.order_state_from_db_model(order_state_db_model) for order_state_db_model in order_state_db_models]
    return ConnexionResponse(body=order_states, status_code=200, content_type="application/json")


def get_order_states(order_id: int, all_available: bool = False) -> ConnexionResponse:
    if not _order_exists(order_id):
        return log_and_respond(404, f"Order with id='{order_id}' was not found. Cannot get its state.")
    else:
        order_state_db_models = db_access.get_records(db_models.OrderStateDBModel, equal_to={'order_id': order_id})
        if not all_available and order_state_db_models:
            order_state_db_models = [order_state_db_models[-1]]
        order_states = [obj_to_db.order_state_from_db_model(order_state_db_model) for order_state_db_model in order_state_db_models]
        return ConnexionResponse(body=order_states, status_code=200, content_type="application/json")


def _order_exists(order_id: int) -> bool:
    order_db_models = db_access.get_records(db_models.OrderDBModel, equal_to={'id': order_id})
    return len(order_db_models) > 0


def _mark_order_as_updated(order_id: int) -> None:
    order_db_model:db_models.OrderDBModel = db_access.get_records(db_models.OrderDBModel, equal_to={'id': order_id})[0]
    order_db_model.updated = True
    db_access.update_record(order_db_model)