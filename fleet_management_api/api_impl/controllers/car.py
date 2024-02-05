from typing import Dict

import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response# type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access


def create_car(car) -> _Response:  # noqa: E501
    """Create a new car.

    The car must have a unique id and name.
    """
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
    else:
        car = _models.Car.from_dict(connexion.request.get_json())
        car_db_model = _api.car_to_db_model(car)
        response = _db_access.add(_db_models.CarDBModel, car_db_model, check_reference_existence={_db_models.PlatformHwIdDBModel: car.platform_hw_id})
        if response.status_code == 200:
            return _api.log_and_respond(200, f"Car (id={car.id}, name='{car.name}) has been sent.")
        else:
            return _api.log_and_respond(response.status_code, f"Car (id={car.id}, name='{car.name}) could not be sent. {response.body}")


def delete_car(car_id: int) -> _Response:
    """Deletes an existing car identified by 'car_id'.

    :param car_id: Id of the car to be deleted.
    """
    orders_response = _orders_related_to_car(car_id)
    if orders_response.status_code != 200:
        return orders_response
    response = _db_access.delete(_db_models.CarDBModel, 'id', car_id)
    if response.status_code == 200:
        msg = f"Car (id={car_id}) has been deleted."
        return _api.log_and_respond(200, msg)
    else:
        msg = f"Car (id={car_id}) could not be deleted. {response.body}"
        return _api.log_and_respond(response.status_code, msg)


def get_car(car_id: int) -> _Response:
    """Get a car identified by 'car_id'."""
    cars = _db_access.get(_db_models.CarDBModel, criteria={'id': lambda x: x==car_id})
    if len(cars) == 0:
        return _api.log_and_respond(404, f"Car with id={car_id} was not found.")
    else:
        _api.log_info(f"Car with id={car_id} was found.")
        car = _api.car_from_db_model(cars[0])
        return _Response(body=cars[0], status_code=200)


def get_cars() -> _Response:  # noqa: E501
    """List all cars."""
    cars = _db_access.get(_db_models.CarDBModel)
    if len(cars) == 0:
        _api.log_info("Listing all cars: no cars found.")
    else:
        _api.log_info(f"Listing all cars: {len(cars)} cars found.")
    return _Response(body=cars, status_code=200)


def update_car(car: Dict|_models.Car) -> _Response:
    """Update an existing car.

    :param car: Updated car object.
    """
    if connexion.request.is_json:
        car = _models.Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = _api.car_to_db_model(car)
        response = _db_access.update(updated_obj=car_db_model)
        if 200 <= response.status_code < 300:
            return _api.log_and_respond(response.status_code, f"Car (id={car.id}) has been succesfully updated")
        else:
            msg = f"Car (id={car.id}) could not be updated. {response.body}"
            return _api.log_and_respond(response.status_code, msg)
    else:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")


def _orders_related_to_car(car_id: int) -> _Response:
    orders = _db_access.get(_db_models.OrderDBModel, criteria={'car_id': lambda x: x==car_id})
    if len(orders) == 0:
        return _Response(200, f"No orders related to car with id = {car_id} were found.")
    else:
        return _Response(400, f"Found {len(orders)} orders related to car with id = {car_id}.")