import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.api_impl.api_logging import log_and_respond
from fleet_management_api.models import PlatformHwId
import fleet_management_api.api_impl.db_models as db_models
import fleet_management_api.database.db_access as db_access
from fleet_management_api.database.db_models import PlatformHwIdDBModel


def get_hw_ids() -> ConnexionResponse:
    return ConnexionResponse(body="not implemented", status_code=501, content_type="text/plain")


def create_hw_id(platform_hw_id) -> ConnexionResponse:
    if connexion.request.is_json:
        platform_hw_id = PlatformHwId.from_dict(connexion.request.get_json())
        platform_hwid_db_model = db_models.platform_hw_id_to_db_model(platform_hw_id)
        response = db_access.add_record(PlatformHwIdDBModel, platform_hwid_db_model)
        if response.status_code == 200:
            return log_and_respond(200, f"Platform HW Id (id={platform_hw_id.id}, name='{platform_hw_id.name}) has been created.")
        elif response.status_code == 400:
            return log_and_respond(response.status_code, f"Platform HW Id (id={platform_hw_id.id}, name='{platform_hw_id.name}) could not be created. {response.body}")

        else:
            return log_and_respond(response.status_code, response.body)
    else:
        return log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
