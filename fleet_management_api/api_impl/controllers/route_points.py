import connexion as _connexion # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response # type: ignore

from fleet_management_api.models import RoutePoints as _RoutePoints
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.api_impl as _api


def get_route_points(route_id: int) -> _Response:
    """Get route points for an existing route identified by 'route_id'."""
    rp_db_models = _db_access.get(_db_models.RoutePointsDBModel, criteria={"route_id": lambda x: x==route_id})
    if len(rp_db_models) == 0:
        return _Response(content_type="text/plain", status_code=404, body=f"Route points for EXISTING route with id={route_id} not found")
    else:
        rp = _api.route_points_from_db_model(rp_db_models[0])
        return _Response(content_type="application/json", status_code=200, body=rp)


def redefine_route_points() -> _Response:
    """Redefine route points for an existing route."""
    if not _connexion.request.is_json:
        return _Response(content_type="text/plain", status_code=400, body="Expected JSON body")
    else:
        rp = _RoutePoints.from_dict(_connexion.request.get_json())
        rp_db_model = _api.route_points_to_db_model(rp)
        existing_route_points = _db_access.get(_db_models.RoutePointsDBModel, criteria={"route_id": lambda x: x==rp.route_id})
        if len(existing_route_points) == 0:
            response = _db_access.add(
                _db_models.RoutePointsDBModel,
                rp_db_model,
                check_reference_existence={_db_models.RouteDBModel: rp.route_id}
            )
            return _api.log_and_respond(response.status_code, response.body)
        else:
            _db_access.delete(_db_models.RoutePointsDBModel, "route_id", existing_route_points[0].id)
            response = _db_access.add(
                _db_models.RoutePointsDBModel,
                rp_db_model,
                check_reference_existence={_db_models.RouteDBModel: rp_db_model.route_id}
            )
            return _api.log_and_respond(response.status_code, response.body)

