import connexion as _connexion  # type: ignore

from fleet_management_api.models import RouteVisualization as _RouteVisualization
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    error as _error,
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
    """Redefine route visualizations for existing routes.

    If a route visualization for a route already exists, it will be replaced.

    If any of the redefinitions fail, the whole operation will be rolled back.

    The visualization can be redefined only if:
    - the route exists.
    """
    if not _connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        request_json = _connexion.request.get_json()
        if not request_json:
            return _log_invalid_request_body_format()

        vis = [_RouteVisualization.from_dict(s) for s in request_json]
        for v in vis:
            if not _db_access.db_object_check(_db_models.RouteDBModel, v.route_id):
                return _error(
                    404,
                    f"Route with ID={v.route_id} does not exist.",
                    title="Object not found",
                )

        existing_vis: list[_db_models.RouteVisualizationDBModel] = _db_access.get(
            _db_models.RouteVisualizationDBModel
        )
        existing_vis_dict: dict[int, _db_models.RouteVisualizationDBModel] = {
            v.route_id: v for v in existing_vis
        }

        vis_db_models = [_obj_to_db.route_visualization_to_db_model(v) for v in vis]
        for v_db in vis_db_models:
            if v_db.route_id in existing_vis_dict:
                id_ = existing_vis_dict[v_db.route_id].id
                v_db.id = id_  # type: ignore
        response = _db_access.update(*vis_db_models)
        if response.status_code == 200:
            _log_info("Route visualizations have been redefined.")
            return _json_response(
                [_obj_to_db.route_visualization_from_db_model(v) for v in response.body]
            )
        else:
            return _log_error_and_respond(
                response.body["detail"], response.status_code, response.body["title"]
            )
