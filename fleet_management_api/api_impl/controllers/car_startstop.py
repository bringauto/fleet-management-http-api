from connexion.lifecycle import ConnexionResponse # type: ignore

from fleet_management_api.models import Car
import fleet_management_api.database.db_access as db_access
import fleet_management_api.api_impl.obj_to_db as obj_to_db
from fleet_management_api.database.db_models import CarDBModel


def startstop_car(car_id):  # noqa: E501
    cars_db_models = db_access.get_records(CarDBModel, equal_to={'id': car_id})
    if cars_db_models:
        car = obj_to_db.car_from_db_model(cars_db_models[0])
        _start_or_stop_car(car)
        return ConnexionResponse(
            status_code=200, body = f"Car (id={car_id}) has been started/stopped.", content_type='text/plain'
        )
    else:
        return ConnexionResponse(
            status_code=404, body = f"Car (id={car_id}) not found.", content_type='text/plain'
        )


def _start_or_stop_car(car: Car) -> None:
    pass