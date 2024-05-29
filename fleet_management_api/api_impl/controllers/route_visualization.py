import connexion as _connexion  # type: ignore

from fleet_management_api.models import RouteVisualization as _RouteVisualization
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    error as _error
)
from fleet_management_api.api_impl.api_logging import (
    log_error_and_respond as _log_error_and_respond,
    log_info as _log_info,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)


def get_route_visualization(route_id: int) -> _Response:
    """Get route visualization for an existing route identified by 'route_id'."""
    rp_db_models = _db_access.get(
        _db_models.RouteVisualizationDBModel, criteria={"route_id": lambda x: x == route_id}
    )
    if len(rp_db_models) == 0:
        return _error(
            404,
            f"Route visualization (route ID={route_id}) was not found.",
            title="Object not found",
        )
    else:
        rp = _obj_to_db.route_visualization_from_db_model(rp_db_models[0])
        _log_info(f"Found route visualization (route ID={route_id}).")
        return _json_response(rp)


def redefine_route_visualizations() -> _Response:
    """Redefine route visualizations for existing routes."""
    if not _connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        request_json = _connexion.request.get_json()
        if not request_json:
            return _log_invalid_request_body_format()

        rp = _RouteVisualization.from_dict(request_json[0])
        rp_db_model = _obj_to_db.route_visualization_to_db_model(rp)
        existing_visualization: list[_db_models.RouteVisualizationDBModel] = _db_access.get(
            _db_models.RouteVisualizationDBModel,
            criteria={"route_id": lambda x: x == rp.route_id}
        )
        if len(existing_visualization) == 0:
            response = _db_access.add(
                rp_db_model,
                checked=[_db_access.db_object_check(_db_models.RouteDBModel, rp.route_id)],
            )
            return _log_error_and_respond(
                response.body["detail"], response.status_code, response.body["title"]
            )
        else:
            _db_access.delete(_db_models.RouteVisualizationDBModel, existing_visualization[0].id)
            response = _db_access.add(
                rp_db_model,
                checked=[_db_access.db_object_check(_db_models.RouteDBModel, rp.route_id)],
            )
            if response.status_code == 200:
                _log_info(
                    f"Route visualization for route with ID={rp.route_id} has been redefined."
                )
                return _json_response(
                    _obj_to_db.route_visualization_from_db_model(response.body[0])
                )
            else:
                return _log_error_and_respond(
                    response.body["detail"], response.status_code, response.body["title"]
                )
