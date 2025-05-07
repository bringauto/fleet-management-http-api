from fleet_management_api.models import PlatformHW as _PlatformHW
from fleet_management_api.database import db_access as _db_access, db_models as _db_models
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_logging import (
    log_info as _log_info,
    log_warning_or_error_and_respond as _log_warning_or_error_and_respond,
    log_info_and_respond as _log_info_and_respond,
)
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
)
from fleet_management_api.response_consts import OBJ_NOT_FOUND as _OBJ_NOT_FOUND
from fleet_management_api.api_impl.controller_decorators import (
    with_processed_request,
    ProcessedRequest as _ProcessedRequest,
)


@with_processed_request(require_data=True)
def create_hws(request: _ProcessedRequest, **kwargs) -> _Response:
    """Create new platform HWs.

    If some of the HWs' creation fails, no objects are added to the server.

    The HW creation can succeed only if:
    - there is no HW with the same name.
    """
    hws = [_PlatformHW.from_dict(p) for p in request.data]
    hw_db_model = [_obj_to_db.hw_to_db_model(p) for p in hws]
    response: _Response = _db_access.add(request.tenants, *hw_db_model)
    if response.status_code == 200:
        inserted_models: list[_PlatformHW] = [
            _obj_to_db.hw_from_db_model(item) for item in response.body
        ]
        for p in inserted_models:
            assert p.id is not None
            _log_info(f"Platform HW (name='{p.name}) has been created.")
        return _json_response(inserted_models)
    else:
        return _log_warning_or_error_and_respond(
            f"Platform HW (names='{[p.name for p in hws]}) could not be created. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )


@with_processed_request
def get_hws(request: _ProcessedRequest, **kwargs) -> _Response:
    """Get all existing platform HWs."""
    hw_id_models = _db_access.get(request.tenants, _db_models.PlatformHWDB)
    platform_hw_ids: list[_PlatformHW] = [
        _obj_to_db.hw_from_db_model(hw_id_model) for hw_id_model in hw_id_models
    ]
    _log_info(f"Found {len(platform_hw_ids)} platform HWs.")
    return _json_response(platform_hw_ids)


@with_processed_request
def get_hw(request: _ProcessedRequest, platform_hw_id: int, **kwargs) -> _Response:
    """Get an existing platform HW identified by 'platformhw_id'."""
    hw_models = _db_access.get(
        request.tenants, _db_models.PlatformHWDB, criteria={"id": lambda x: x == platform_hw_id}
    )
    hws = [_obj_to_db.hw_from_db_model(hw_id_model) for hw_id_model in hw_models]
    if len(hws) == 0:
        return _log_info_and_respond(
            f"Platform HW with ID={platform_hw_id} was not found.",
            404,
            title=_OBJ_NOT_FOUND,
        )
    else:
        _log_info(f"Found {len(hws)} platform HWs with ID={platform_hw_id}")
        return _json_response(hws[0])


@with_processed_request
def delete_hw(request: _ProcessedRequest, platform_hw_id: int, **kwargs) -> _Response:
    """Delete an existing platform HW identified by 'platformhw_id'.

    The platform HW cannot be deleted if assigned to a Car.
    """
    if _db_access.exists(request.tenants, _db_models.CarDB, criteria={"platform_hw_id": lambda x: x == platform_hw_id}):  # type: ignore
        return _log_info_and_respond(
            f"Platform HW with ID={platform_hw_id} cannot be deleted because it is assigned to a car.",
            400,
            title="Cannot delete object",
        )
    response = _db_access.delete(request.tenants, _db_models.PlatformHWDB, platform_hw_id)
    if response.status_code == 200:
        return _log_info_and_respond(f"Platform HW with ID={platform_hw_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_warning_or_error_and_respond(
            f"Could not delete platform HW with ID={platform_hw_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
