from typing import Tuple, List, Dict
import logging

import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models import Car, MobilePhone
from fleet_management_api.database.db_models import CarDBModel
from fleet_management_api.database.db_access import (
    send_to_database,
    retrieve_from_database
)


API_LOGGER_NAME = "werkzeug"


def create_car(car: Dict) -> ConnexionResponse:  # noqa: E501
    if connexion.request.is_json:
        car: Car = Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = car_to_db_model(car)
        response = send_to_database(CarDBModel, car_db_model)
        if response.status_code == 200:
            _log_info(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) has been created.")
            return 'Car was succesfully created.'
        elif response.status_code == 400:
            _log_error(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) could not be created. {response.body}")
            return response
    else:
        _log_error(f"Invalid request format: {connexion.request.data}. JSON is required")
        return 'Invalid request format.'


def get_cars() -> Tuple[List[Car], int]:  # noqa: E501
    cars = retrieve_from_database(CarDBModel)
    return cars, 200


def car_to_db_model(car: Car) -> CarDBModel:
    if car.car_admin_phone is None:
        car_mobile_phone = None
    else:
        car_mobile_phone = car.car_admin_phone.to_dict()
    return CarDBModel(
        id=car.id,
        name=car.name,
        platform_id=car.platform_id,
        car_admin_phone=car_mobile_phone,
        default_route_id=car.default_route_id
    )


def car_from_db_model(car_db_model: CarDBModel) -> Car:
    if car_db_model.car_admin_phone is None:
        car_mobile_phone = None
    else:
        car_mobile_phone = MobilePhone.from_dict(car_db_model.car_admin_phone)
    return Car(
        id=car_db_model.id,
        name=car_db_model.name,
        platform_id=car_db_model.platform_id,
        car_admin_phone=car_mobile_phone,
        default_route_id=car_db_model.default_route_id
    )


def _log_info(message: str) -> None:
    logger = logging.getLogger(API_LOGGER_NAME)
    logger.info(message)

def _log_error(message: str) -> None:
    logger = logging.getLogger(API_LOGGER_NAME)
    logger.error(message)