from typing import List

import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse # type: ignore

from fleet_management_api.api_impl.api_logging import log_and_respond, log_info
import fleet_management_api.api_impl.obj_to_db as obj_to_db
from fleet_management_api.models import PlatformHwId

import fleet_management_api.database.db_access as db_access
from fleet_management_api.database.db_models import PlatformHwIdDBModel


def create_hw_id(platform_hw_id) -> ConnexionResponse:
    if connexion.request.is_json:
        platform_hw_id = PlatformHwId.from_dict(connexion.request.get_json())
        platform_hwid_db_model = obj_to_db.platform_hw_id_to_db_model(platform_hw_id)
        response = db_access.add(PlatformHwIdDBModel, platform_hwid_db_model)
        if response.status_code == 200:
            return log_and_respond(200, f"Platform HW Id (id={platform_hw_id.id}, name='{platform_hw_id.name}) has been created.")
        elif response.status_code == 400:
            return log_and_respond(response.status_code, f"Platform HW Id (id={platform_hw_id.id}, name='{platform_hw_id.name}) could not be created. {response.body}")

        else:
            return log_and_respond(response.status_code, response.body)
    else:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")


def get_hw_ids() -> ConnexionResponse:
    hw_id_moodels = db_access.get(PlatformHwIdDBModel)
    platform_hw_ids: List[PlatformHwId] = [obj_to_db.platform_hw_id_from_db_model(hw_id_model) for hw_id_model in hw_id_moodels]
    return ConnexionResponse(body=platform_hw_ids, status_code=200, content_type="application/json")


def get_hw_id(platformhwid_id: int) -> ConnexionResponse:
    hw_id_moodels = db_access.get(PlatformHwIdDBModel, criteria={"id": lambda x: x==platformhwid_id})
    platform_hw_ids = [obj_to_db.platform_hw_id_from_db_model(hw_id_model) for hw_id_model in hw_id_moodels]
    if len(platform_hw_ids) == 0:
        return log_and_respond(404, f"Platform HW Id  with id={platformhwid_id} was not found.")
    else:
        log_info(f"Found {len(platform_hw_ids)} platform HW Ids with id={platformhwid_id}")
        return ConnexionResponse(body=platform_hw_ids[0], status_code=200, content_type="application/json")


def delete_hw_id(platformhwid_id: int) -> ConnexionResponse:
    response = db_access.delete(PlatformHwIdDBModel, id_name="id", id_value=platformhwid_id)
    if response.status_code == 200:
        return log_and_respond(200, f"Platform HW Id with id={platformhwid_id} has been deleted.")
    elif response.status_code == 404:
        return log_and_respond(404, f"Platform HW Id with id={platformhwid_id} was not found.")
    else:
        return log_and_respond(response.status_code, f"Could not delete platform HW id (id={platformhwid_id}). {response.json()}")

