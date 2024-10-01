import connexion  # type: ignore

from fleet_management_api.models import PlatformHW as _PlatformHW
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.api_impl.obj_to_db as _obj_to_db
from ...api_impl.api_logging import (
    log_info as _log_info,
    log_error_and_respond as _log_error_and_respond,
    log_info_and_respond as _log_info_and_respond,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
from ...api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
)
from ...response_consts import OBJ_NOT_FOUND as _OBJ_NOT_FOUND


def create_hws() -> _Response:
    """Create new platform HWs.

    If some of the HWs' creation fails, no objects are added to the server.

    The HW creation can succeed only if:
    - there is no HW with the same name.
    """
    if not connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        hws = [_PlatformHW.from_dict(p) for p in connexion.request.get_json()]
        hw_db_model = [_obj_to_db.hw_to_db_model(p) for p in hws]
        response: _Response = _db_access.add(*hw_db_model)
        if response.status_code == 200:
            inserted_models: list[_PlatformHW] = [
                _obj_to_db.hw_from_db_model(item) for item in response.body
            ]
            for p in inserted_models:
                assert p.id is not None
                _log_info(f"Platform HW (name='{p.name}) has been created.")
            return _json_response(inserted_models)
        else:
            return _log_error_and_respond(
                f"Platform HW (names='{[p.name for p in hws]}) could not be created. {response.body['detail']}",
                response.status_code,
                response.body["title"],
            )


def get_hws() -> _Response:
    """Get all existing platform HWs."""
    hw_id_moodels = _db_access.get(_db_models.PlatformHWDBModel)
    hw_ids: list[_PlatformHW] = [
        _obj_to_db.hw_from_db_model(hw_id_model) for hw_id_model in hw_id_moodels
    ]
    _log_info(f"Found {len(hw_ids)} platform HWs.")
    return _json_response(hw_ids)


def get_hw(platform_hw_id: int) -> _Response:
    """Get an existing platform HW identified by 'platformhw_id'."""
    hw_models = _db_access.get(_db_models.PlatformHWDBModel, criteria={"id": lambda x: x == platform_hw_id})
    hws = [_obj_to_db.hw_from_db_model(hw_id_model) for hw_id_model in hw_models]
    if len(hws) == 0:
        return _log_error_and_respond(
            f"Platform HW with ID={platform_hw_id} was not found.",
            404,
            title=_OBJ_NOT_FOUND,
        )
    else:
        _log_info(f"Found {len(hws)} platform HWs with ID={platform_hw_id}")
        return _json_response(hws[0])


def delete_hw(platform_hw_id: int) -> _Response:
    """Delete an existing platform HW identified by 'platformhw_id'.

    The platform HW cannot be deleted if assigned to a Car.
    """
    if _db_access.exists(_db_models.CarDBModel, criteria={"platform_hw_id": lambda x: x == platform_hw_id}):  # type: ignore
        return _log_error_and_respond(
            f"Platform HW with ID={platform_hw_id} cannot be deleted because it is assigned to a car.",
            400,
            title="Cannot delete object",
        )
    response = _db_access.delete(_db_models.PlatformHWDBModel, platform_hw_id)
    if response.status_code == 200:
        return _log_info_and_respond(f"Platform HW with ID={platform_hw_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_error_and_respond(
            f"Could not delete platform HW with ID={platform_hw_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
