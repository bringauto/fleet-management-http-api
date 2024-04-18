import connexion  # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.api_impl.controllers.car_state import add_car_state_from_argument as _add_car_state_from_argument


def create_car() -> _api.Response:  # noqa: E501
    """Create a new car.

    The car must have a unique ID and name.
    """
    if not connexion.request.is_json:
        _api.log_invalid_request_body_format()
    else:
        car = _models.Car.from_dict(connexion.request.get_json())
        car_db_model = _api.car_to_db_model(car)
        response = _db_access.add(
            car_db_model,
            checked=[
                _db_access.db_object_check(_db_models.PlatformHWDBModel, id_=car.platform_hw_id),
                _db_access.db_object_check(
                    _db_models.RouteDBModel, id_=car.default_route_id, allow_nonexistence=True
                ),
            ],
        )
        if response.status_code == 200:
            inserted_model = _api.car_from_db_model(response.body[0])
            _api.log_info(f"Car (ID={inserted_model.id}, name='{car.name}) has been created.")
            _create_default_car_state(inserted_model.id)
            return _api.json_response(inserted_model)
        else:
            return _api.log_error_and_respond(
                code=response.status_code,
                msg=f"Car (name='{car.name}) could not be created. {response.body['detail']}",
                title=response.body['title']
            )


def delete_car(car_id: int) -> _api.Response:
    """Deletes an existing car identified by 'car_id'.

    :param car_id: ID of the car to be deleted.
    """
    response = _db_access.delete(_db_models.CarDBModel, car_id)
    if response.status_code == 200:
        msg = f"Car (ID={car_id}) has been deleted."
        return _api.log_info_and_respond(msg)
    else:
        msg = f"Car (ID={car_id}) could not be deleted. {response.body['detail']}"
        return _api.log_error_and_respond(msg, response.status_code, response.body['title'])


def get_car(car_id: int) -> _api.Response:
    """Get a car identified by 'car_id'."""
    cars = _db_access.get(
        _db_models.CarDBModel,
        criteria={"id": lambda x: x == car_id},
        omitted_relationships=[_db_models.CarDBModel.states, _db_models.CarDBModel.orders],
    )
    if len(cars) == 0:
        return _api.log_error_and_respond(f"Car with ID={car_id} was not found.", 404, title="Object was not found")
    else:
        _api.log_info(f"Car with ID={car_id} was found.")
        return _api.json_response(_api.car_from_db_model(cars[0]))


def get_cars() -> _api.Response:  # noqa: E501
    """List all cars."""
    cars = _db_access.get(
        _db_models.CarDBModel,
        omitted_relationships=[_db_models.CarDBModel.states, _db_models.CarDBModel.orders],
    )
    if len(cars) == 0:
        _api.log_info("Listing all cars: no cars found.")
    else:
        _api.log_info(f"Listing all cars: {len(cars)} cars found.")
    return _api.json_response([_api.car_from_db_model(c) for c in cars])


def update_car(car: dict | _models.Car) -> _api.Response:
    """Update an existing car.

    :param car: Updated car object.
    """
    if connexion.request.is_json:
        car = _models.Car.from_dict(connexion.request.get_json())  # noqa: E501
        car_db_model = _api.car_to_db_model(car)
        response = _db_access.update(updated=car_db_model)
        if response.status_code == 200:
            return _api.log_info_and_respond(
                f"Car (ID={car.id}) has been succesfully updated."
            )
        else:
            msg = f"Car (ID={car.id}) could not be updated. {response.body['detail']}"
            return _api.log_error_and_respond(msg, response.status_code, response.body['title'])
    else:
        return _api.log_invalid_request_body_format()


def _create_default_car_state(car_id: int) -> _api.Response:
    car_state = _models.CarState(
        status=_models.CarStatus.OUT_OF_ORDER,
        car_id=car_id,
        fuel=0,
        speed=0.0
    )
    response = _add_car_state_from_argument(car_state)
    return response