from fleet_management_api.models import RouteVisualization as _RouteVisualization
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.db_models import (
    RouteDB as _RouteDB,
    RouteVisualizationDB as _RouteVisDB,
)
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    error as _error,
)
from fleet_management_api.api_impl.api_logging import (
    log_error_and_respond as _log_error_and_respond,
    log_info_and_respond as _log_info_and_respond,
    log_info as _log_info,
)
from fleet_management_api.response_consts import OBJ_NOT_FOUND as _OBJ_NOT_FOUND
from fleet_management_api.api_impl.controller_decorators import (
    controller_with_tenants,
    controller_with_tenants_and_data,
    ProcessedRequest as _ProcessedRequest,
)


@controller_with_tenants
def get_route_visualization(request: _ProcessedRequest, route_id: int, **kwargs) -> _Response:
    """Get route visualization for an existing route identified by 'route_id'."""
    rp_db_models = _db_access.get(
        request.tenants, _RouteVisDB, criteria={"route_id": lambda x: x == route_id}
    )
    if len(rp_db_models) == 0:
        return _error(
            404,
            f"Route visualization (route ID={route_id}) was not found.",
            title=_OBJ_NOT_FOUND,
        )
    else:
        rp = _obj_to_db.route_visualization_from_db_model(rp_db_models[0])
        _log_info(f"Found route visualization (route ID={route_id}).")
        return _json_response(rp)


@controller_with_tenants_and_data
def redefine_route_visualizations(request: _ProcessedRequest, **kwargs) -> _Response:
    """Redefine route visualizations for existing routes.

    If a route visualization for a route already exists, it will be replaced.

    If any of the redefinitions fail, the whole operation will be rolled back.

    The visualization can be redefined only if:
    - the route exists.
    """
    vis = [_RouteVisualization.from_dict(s) for s in request.data]
    for v in vis:
        if not _db_access.db_object_check(_RouteDB, v.route_id):
            return _error(
                404,
                f"Route with ID={v.route_id} does not exist.",
                title=_OBJ_NOT_FOUND,
            )

    existing_vis: list[_RouteVisDB] = _db_access.get(request.tenants, _RouteVisDB)
    existing_vis_dict: dict[int, _RouteVisDB] = {v.route_id: v for v in existing_vis}
    for v in vis:
        if v.route_id in existing_vis_dict:
            id_ = existing_vis_dict[v.route_id].id
            v.id = id_  # type: ignore
        else:
            return _log_info_and_respond(
                f"Route visualization for route with ID={v.route_id} does not exist. Cannot redefine visualizations.",
                404,
                title=_OBJ_NOT_FOUND,
            )

    vis_db_models = [_obj_to_db.route_visualization_to_db_model(v) for v in vis]
    response = _db_access.update(request.tenants, *vis_db_models)
    if response.status_code == 200:
        inserted_vis = [_obj_to_db.route_visualization_from_db_model(m) for m in response.body]
        for v in inserted_vis:
            assert v.id is not None
            _log_info(f"Route visualization (ID={v.id}) has been succesfully redefined.")
        return _json_response(inserted_vis)
    else:
        return _log_error_and_respond(
            response.body["detail"], response.status_code, response.body["title"]
        )
