from typing import List

import connexion  # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

import fleet_management_api.api_impl as _api
from fleet_management_api.models import PlatformHW as _PlatformHW
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models


def create_hw() -> _Response:
    """Post a new platform HW. The platform HW must have a unique id."""
    if not connexion.request.is_json:
        _api.log_invalid_request_body_format()
    else:
        platform_hw = _PlatformHW.from_dict(connexion.request.get_json())
        platform_hw_db_model = _api.platform_hw_to_db_model(platform_hw)
        response = _db_access.add(platform_hw_db_model)
        if response.status_code == 200:
            _api.log_info(f"Platform HW (name='{platform_hw.name}) has been created.")
            inserted_model = _api.platform_hw_from_db_model(response.body)
            return _Response(body=inserted_model, status_code=200, content_type="application/json")
        else:
            return _api.log_and_respond(
                response.status_code,
                f"Platform HW (name='{platform_hw.name}) could not be created. {response.body}",
            )


def get_hws() -> _Response:
    """Get all existing platform HWs."""
    hw_id_moodels = _db_access.get(_db_models.PlatformHWDBModel)
    platform_hw_ids: List[_PlatformHW] = [
        _api.platform_hw_from_db_model(hw_id_model) for hw_id_model in hw_id_moodels
    ]
    _api.log_info(f"Found {len(platform_hw_ids)} platform HWs.")
    return _Response(body=platform_hw_ids, status_code=200, content_type="application/json")


def get_hw(platform_hw_id: int) -> _Response:
    """Get an existing platform HW identified by 'platformhw_id'."""
    hw_models = _db_access.get(
        _db_models.PlatformHWDBModel, criteria={"id": lambda x: x == platform_hw_id}
    )
    platform_hws = [_api.platform_hw_from_db_model(hw_id_model) for hw_id_model in hw_models]
    if len(platform_hws) == 0:
        return _api.log_and_respond(404, f"Platform HW  with ID={platform_hw_id} was not found.")
    else:
        _api.log_info(f"Found {len(platform_hws)} platform HWs with ID={platform_hw_id}")
        return _Response(body=platform_hws[0], status_code=200, content_type="application/json")


def delete_hw(platform_hw_id: int) -> _Response:
    """Delete an existing platform HW identified by 'platformhw_id'.

    The platform HW cannot be deleted if assigned to a Car.
    """
    if _db_access.get(_db_models.CarDBModel, criteria={"platform_hw_id": lambda x: x == platform_hw_id}):  # type: ignore
        return _api.log_and_respond(
            400,
            f"Platform HW with ID={platform_hw_id} cannot be deleted because it is assigned to a car.",
        )
    response = _db_access.delete(_db_models.PlatformHWDBModel, platform_hw_id)
    if response.status_code == 200:
        return _api.log_and_respond(200, f"Platform HW with ID={platform_hw_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _api.log_and_respond(
            response.status_code,
            f"Could not delete platform HW with ID={platform_hw_id}{note}. {response.body}",
        )
