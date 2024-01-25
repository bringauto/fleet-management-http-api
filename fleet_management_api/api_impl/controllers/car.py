import connexion # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response# type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access


def create_car(car) -> _Response:  # noqa: E501
    if not connexion.request.is_json:
        return _api.log_and_respond(400, f"Invalid request format: {connexion.request.data}. JSON is required")
    else:
        car = _models.Car.from_dict(connexion.request.get_json())
        car_db_model = _api.car_to_db_model(car)
        response = _db_access.add(_db_models.CarDBModel, car_db_model)
        if response.status_code == 200:
            return _api.log_and_respond(200, f"Car (id={car.id}, name='{car.name}) has been sent.")
        elif response.status_code == 400:
            return _api.log_and_respond(response.status_code, f"Car (id={car.id}, name='{car.name}) could not be sent. {response.body}")
        else:
            return _api.log_and_respond(response.status_code, response.body)


def delete_car(car_id) -> _Response:
    response = _db_access.delete(_db_models.CarDBModel, 'id', car_id)
    if 200 <= response.status_code < 300:
        msg = f"Car (id={car_id}) has been deleted."
        _api.log_info(msg)
        return _Response(body="Car has been succesfully deleted", status_code=200)
    else:
        msg = f"Car (id={car_id}) could not be deleted. {response.body}"
        _api.log_error(msg)
        return _Response(body=msg, status_code=response.status_code)


def get_car(car_id) -> _Response:
    cars = _db_access.get(_db_models.CarDBModel, criteria={'id': lambda x: x==car_id})
    if len(cars) == 0:
        return _Response(body=f"Car with id={car_id} was not found.", status_code=404)
    else:
        return _Response(body=cars[0], status_code=200)


def get_cars() -> _Response:  # noqa: E501
    cars = _db_access.get(_db_models.CarDBModel)
    return _Response(body=cars, status_code=200)


def update_car(car) -> _Response:
    if connexion.request.is_json:
        car = _models.Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = _api.car_to_db_model(car)
        response = _db_access.update(updated_obj=car_db_model)
        if 200 <= response.status_code < 300:
            _api.log_info(f"Car (id={car.id} has been suchas been succesfully updated")
            return _Response(body=f"Car (id='{car.id}') has been succesfully updated", status_code=200)
        else:
            msg = f"Car (id={car.id}) could not be updated. {response.body}"
            _api.log_error(msg)
            return _Response(body=msg, status_code=response.status_code)
    else:
        _api.log_error(f"Invalid request format: {connexion.request.data}. JSON is required")
        return _Response(body='Invalid request format.', status_code=400)


