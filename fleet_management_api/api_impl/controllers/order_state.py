from typing import Optional, Dict, Callable, Any

import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models


def create_order_state(order_state) -> _Response:
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")

    order_state = _models.OrderState.from_dict(connexion.request.get_json())
    if not _order_exists(order_state.order_id):
        return _api.log_and_respond(404, f"Order with id='{order_state.order_id}' was not found.")

    order_state_db_model = _api.order_state_to_db_model(order_state)
    response = _db_access.add(_db_models.OrderStateDBModel, order_state_db_model)
    if response.status_code == 200:
        _mark_order_as_updated(order_state.order_id)
        _remove_old_states()
        return _api.log_and_respond(200, f"Order state (id={order_state.id}) has been sent.")
    else:
        return _api.log_and_respond(response.status_code, f"Order state (id={order_state.id}) could not be sent. {response.body}")


def get_all_order_states(wait: bool = False, since: int = 0) -> _Response:
    return _get_order_states({}, wait, since)


def get_order_states(order_id: int, wait: bool = False, since: int = 0) -> _Response:
    if not _order_exists(order_id):
        return _api.log_and_respond(404, f"Order with id='{order_id}' was not found. Cannot get its state.")
    else:
        criteria: Dict[str, Callable[[Any],bool]] = {'order_id': lambda x: x==order_id}
        return _get_order_states(criteria, wait, since)


def _get_order_states(criteria: Dict[str, Callable[[Any],bool]], wait: bool = False, since: int = 0) -> _Response:
    criteria['timestamp'] = lambda x: x>=since
    order_state_db_models = _db_access.get(_db_models.OrderStateDBModel, wait=wait, criteria=criteria)

    order_states = [_api.order_state_from_db_model(order_state_db_model) for order_state_db_model in order_state_db_models]
    return _Response(body=order_states, status_code=200, content_type="application/json")


def _remove_old_states() -> _Response:
    order_state_db_models = _db_access.get(_db_models.OrderStateDBModel)
    extras = max(len(order_state_db_models) - _db_models.OrderStateDBModel.max_n_of_stored_states(), 0)
    if extras>0:
        response = _db_access.delete_n(_db_models.OrderStateDBModel, n=extras, id_name='timestamp', start_from="minimum")
        if response.status_code != 200:
            return _api.log_and_respond(response.status_code, response.body)
        else:
            return _api.log_and_respond(200, "Removing oldest order state.")
    else:
        return _Response(status_code=200, content_type="text/plain", body="")


def _order_exists(order_id: int) -> bool:
    order_db_models = _db_access.get(_db_models.OrderDBModel,criteria={'id': lambda x: x==order_id})
    return len(order_db_models) > 0


def _mark_order_as_updated(order_id: int) -> None:
    order_db_model:_db_models.OrderDBModel = _db_access.get(_db_models.OrderDBModel, criteria={'id': lambda x: x==order_id})[0]
    order_db_model.updated = True
    _db_access.update(order_db_model)
