import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.api_impl.api_logging import log_info, log_error
from fleet_management_api.models import Order
import fleet_management_api.api_impl.db_models as db_models
import fleet_management_api.database.db_access as db_access
from fleet_management_api.database.db_models import PlatformHwIdDBModel


def get_hw_ids() -> ConnexionResponse:
    return ConnexionResponse(body="not implemented", status_code=501, content_type="text/plain")


def create_hw_id(platform_hw_id) -> ConnexionResponse:
    if connexion.request.is_json:
        car = Order.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = db_models.car_to_db_model(car)
        response = db_access.add_record(PlatformHwIdDBModel, car_db_model)
        if response.status_code == 200:
            log_info(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) has been created.")
            return ConnexionResponse(body=f"Car with id='{car.id}' was succesfully created.", status_code=200)
        elif response.status_code == 400:
            log_error(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) could not be created. {response.body}")
            return response
    else:
        log_error(f"Invalid request format: {connexion.request.data}. JSON is required")
        return ConnexionResponse(body='Invalid request format.', status_code=400)

    return ConnexionResponse(body="not implemented", status_code=501, content_type="text/plain")