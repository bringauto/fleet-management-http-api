from typing import List

import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response# type: ignore

import fleet_management_api.api_impl as _api
from fleet_management_api.models import PlatformHwId as _PlatformHwId
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models


def create_hw_id(platform_hw_id) -> _Response:
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
    else:
        platform_hw_id = _PlatformHwId.from_dict(connexion.request.get_json())
        platform_hwid_db_model = _api.platform_hw_id_to_db_model(platform_hw_id)
        response = _db_access.add(_db_models.PlatformHwIdDBModel, platform_hwid_db_model)
        if response.status_code == 200:
            return _api.log_and_respond(200, f"Platform HW Id (id={platform_hw_id.id}, name='{platform_hw_id.name}) has been created.")
        else:
            return _api.log_and_respond(
                response.status_code,
                f"Platform HW Id (id={platform_hw_id.id}, name='{platform_hw_id.name}) could not be created. {response.body}")


def get_hw_ids() -> _Response:
    hw_id_moodels = _db_access.get(_db_models.PlatformHwIdDBModel)
    platform_hw_ids: List[_PlatformHwId] = [_api.platform_hw_id_from_db_model(hw_id_model) for hw_id_model in hw_id_moodels]
    return _Response(body=platform_hw_ids, status_code=200, content_type="application/json")


def get_hw_id(platformhwid_id: int) -> _Response:
    hw_id_moodels = _db_access.get(_db_models.PlatformHwIdDBModel, criteria={"id": lambda x: x==platformhwid_id})
    platform_hw_ids = [_api.platform_hw_id_from_db_model(hw_id_model) for hw_id_model in hw_id_moodels]
    if len(platform_hw_ids) == 0:
        return _api.log_and_respond(404, f"Platform HW Id  with id={platformhwid_id} was not found.")
    else:
        _api.log_info(f"Found {len(platform_hw_ids)} platform HW Ids with id={platformhwid_id}")
        return _Response(body=platform_hw_ids[0], status_code=200, content_type="application/json")


def delete_hw_id(platformhwid_id: int) -> _Response:
    response = _db_access.delete(_db_models.PlatformHwIdDBModel, id_name="id", id_value=platformhwid_id)
    if response.status_code == 200:
        return _api.log_and_respond(200, f"Platform HW Id with id={platformhwid_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _api.log_and_respond(response.status_code, f"Could not delete platform HW id with id={platformhwid_id}{note}. {response.body}")

