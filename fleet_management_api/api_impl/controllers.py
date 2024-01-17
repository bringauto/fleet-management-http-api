from typing import Dict

import connexion
from connexion.lifecycle import ConnexionResponse

import fleet_management_api.api_impl.obj_to_db as obj_to_db
from fleet_management_api.models import Car
from fleet_management_api.database.db_models import CarDBModel
import fleet_management_api.database.db_access as db_access
from fleet_management_api.api_impl.api_logging import log_info, log_error


def create_car(car: Dict) -> ConnexionResponse:  # noqa: E501
    if connexion.request.is_json:
        car: Car = Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = obj_to_db.car_to_db_model(car)
        response = db_access.send_to_database(CarDBModel, car_db_model)
        if response.status_code == 200:
            log_info(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) has been created.")
            return 'Car was succesfully created.'
        elif response.status_code == 400:
            log_error(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) could not be created. {response.body}")
            return response
    else:
        log_error(f"Invalid request format: {connexion.request.data}. JSON is required")
        return ConnexionResponse(body='Invalid request format.', status_code=400)


def get_cars() -> ConnexionResponse:  # noqa: E501
    cars = db_access.retrieve_from_database(CarDBModel)
    return ConnexionResponse(body=cars, status_code=200)


def update_car(car) -> ConnexionResponse:
    if connexion.request.is_json:
        car = Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = obj_to_db.car_to_db_model(car)
        response = db_access.update_record(id_name="id", id_value=car.id, updated_obj=car_db_model)
        if response.status_code == 200:
            log_info(f"Car (id={car.id} has been sucessfully updated.")
            return ConnexionResponse(body="Car was succesfully updated", status_code=200)
        else:
            msg = f"Car (id={car.id}) could not be updated. {response.body}"
            log_error(msg)
            return ConnexionResponse(body=msg, status_code=response.status_code)
    else:
        log_error(f"Invalid request format: {connexion.request.data}. JSON is required")
        return ConnexionResponse(body='Invalid request format.', status_code=400)
