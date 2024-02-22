import connexion as _connexion  # type: ignore

from fleet_management_api.models import RouteVisualization as _RouteVisualization
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.api_impl as _api


def get_route_visualization(route_id: int) -> _api.Response:
    """Get route visualization for an existing route identified by 'route_id'."""
    rp_db_models = _db_access.get(
        _db_models.RouteVisualizationDBModel, criteria={"route_id": lambda x: x == route_id}
    )
    if len(rp_db_models) == 0:
        return _api.text_response(404, f"Route visualization for EXISTING route with ID={route_id} not found.")
    else:
        rp = _api.route_visualization_from_db_model(rp_db_models[0])
        _api.log_info(
            f"Found route visualization for route with ID={route_id} containing {len(rp.points)} points."
        )
        return _api.json_response(200, rp)


def redefine_route_visualization() -> _api.Response:
    """Redefine route visualization for an existing route."""
    if not _connexion.request.is_json:
        return _api.log_invalid_request_body_format()
    else:
        rp = _RouteVisualization.from_dict(_connexion.request.get_json())
        rp_db_model = _api.route_visualization_to_db_model(rp)
        existing_visualization = _db_access.get(
            _db_models.RouteVisualizationDBModel, criteria={"route_id": lambda x: x == rp.route_id}
        )
        if len(existing_visualization) == 0:
            response = _db_access.add(
                rp_db_model,
                checked=[
                    _db_access.db_object_check(_db_models.RouteDBModel, rp.route_id)
                ],
            )
            return _api.log_and_respond(response.status_code, response.body)
        else:
            _db_access.delete(_db_models.RouteVisualizationDBModel, existing_visualization[0].id)
            response = _db_access.add(
                rp_db_model,
                checked=[
                    _db_access.db_object_check(_db_models.RouteDBModel, rp.route_id)
                ],
            )
            if response.status_code == 200:
                _api.log_info(f"Route visualization for route with ID={rp.route_id} have been redefined.")
                return _api.json_response(200, _api.route_visualization_from_db_model(response.body[0]))
            else:
                return _api.log_and_respond(response.status_code, response.body)
