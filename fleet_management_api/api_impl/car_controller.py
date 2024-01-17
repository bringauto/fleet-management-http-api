from typing import Dict

import connexion
from connexion.lifecycle import ConnexionResponse

import fleet_management_api.api_impl.db_models as db_models
from fleet_management_api.models import Car
from fleet_management_api.database.db_models import CarDBModel
import fleet_management_api.database.db_access as db_access
from fleet_management_api.api_impl.api_logging import log_info, log_error


def create_car(car: Dict) -> ConnexionResponse:  # noqa: E501
    if connexion.request.is_json:
        car: Car = Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = db_models.car_to_db_model(car)
        response = db_access.add_record(CarDBModel, car_db_model)
        if response.status_code == 200:
            log_info(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) has been created.")
            return ConnexionResponse(body=f"Car with id='{car.id}' was succesfully created.", status_code=200)
        elif response.status_code == 400:
            log_error(f"Car (id={car.id}, name='{car.name}, platform_id={car.platform_id}) could not be created. {response.body}")
            return response
    else:
        log_error(f"Invalid request format: {connexion.request.data}. JSON is required")
        return ConnexionResponse(body='Invalid request format.', status_code=400)


def delete_car(car_id) -> ConnexionResponse:
    response = db_access.delete_record(CarDBModel, 'id', car_id)
    if 200 <= response.status_code < 300:
        msg = f"Car (id={car_id}) has been deleted."
        log_info(msg)
        return ConnexionResponse(body="Car has been succesfully deleted", status_code=200)
    else:
        msg = f"Car (id={car_id}) could not be deleted. {response.body}"
        log_error(msg)
        return ConnexionResponse(body=msg, status_code=response.status_code)


def get_car(car_id) -> ConnexionResponse:
    cars = db_access.get_records(CarDBModel, equal_to={'id': car_id})
    if len(cars) == 0:
        return ConnexionResponse(body=f"Car with id={car_id} was not found.", status_code=404)
    else:
        return ConnexionResponse(body=cars[0], status_code=200)


def get_cars() -> ConnexionResponse:  # noqa: E501
    cars = db_access.get_records(CarDBModel)
    return ConnexionResponse(body=cars, status_code=200)


def update_car(car) -> ConnexionResponse:
    if connexion.request.is_json:
        car = Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = db_models.car_to_db_model(car)
        response = db_access.update_record(id_name="id", id_value=car.id, updated_obj=car_db_model)
        if 200 <= response.status_code < 300:
            log_info(f"Car (id={car.id} has been suchas been succesfully updated")
            return ConnexionResponse(body=f"Car (id='{car.id}') has been succesfully updated", status_code=200)
        else:
            msg = f"Car (id={car.id}) could not be updated. {response.body}"
            log_error(msg)
            return ConnexionResponse(body=msg, status_code=response.status_code)
    else:
        log_error(f"Invalid request format: {connexion.request.data}. JSON is required")
        return ConnexionResponse(body='Invalid request format.', status_code=400)


