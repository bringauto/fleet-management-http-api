import connexion  # type: ignore

import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.api_impl.controllers.car_state import (
    create_car_states_from_argument_and_post as _create_car_state_from_argument_and_post,
)
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
)
from fleet_management_api.api_impl.api_logging import (
    log_info as _log_info,
    log_info_and_respond as _log_info_and_respond,
    log_error_and_respond as _log_error_and_respond,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
import fleet_management_api.api_impl.obj_to_db as _obj_to_db


def create_cars() -> _Response:  # noqa: E501
    """Create new cars.

    If some of the cars' creation fails, no cars are added to the server.

    The car creation can succeed only if:
    - the platform HW exists,
    - the default route exists, if it is specified,
    - the car name is unique.
    - the platform HW is not referenced by any existing car.
    """
    if not connexion.request.is_json:
        _log_invalid_request_body_format()
    request = connexion.request.get_json()
    if not request:
        return _json_response([])
    else:
        cars: list[_models.Car] = []
        for car_dict in connexion.request.get_json():
            car_dict["lastState"] = None
            car = _models.Car.from_dict(car_dict)
            cars.append(car)

        car_db_models = []
        checked = []
        for car in cars:
            car_db_models.append(_obj_to_db.car_to_db_model(car))
            checked.append(
                _db_access.db_object_check(_db_models.PlatformHWDBModel, id_=car.platform_hw_id)
            )
            checked.append(
                _db_access.db_object_check(
                    _db_models.RouteDBModel,
                    id_=car.default_route_id,
                    allow_nonexistence=True,
                )
            )

        response = _db_access.add(*car_db_models, checked=checked)
        if response.status_code == 200:
            posted_db_models: list[_db_models.CarDBModel] = response.body
            posted_cars = []
            for posted_db_model in posted_db_models:
                assert posted_db_model.id is not None
                db_state = _post_default_car_state(posted_db_model.id).body[0]
                state = _obj_to_db.car_state_from_db_model(db_state)
                posted_car = _obj_to_db.car_from_db_model(posted_db_model, state)
                msg = f"Car (ID={posted_car.id}, name='{posted_car.name}') has been created."
                print(msg)
                _log_info(f"Car (ID={posted_car.id}, name='{posted_car.name}) has been created.")
                posted_cars.append(posted_car)
            return _json_response(posted_cars)
        else:
            return _log_error_and_respond(
                code=response.status_code,
                msg=f"Cars could not be created. {response.body['detail']}",
                title=response.body["title"],
            )


def delete_car(car_id: int) -> _Response:
    """Deletes an existing car identified by 'car_id'.

    :param car_id: ID of the car to be deleted.
    """
    response = _db_access.delete(_db_models.CarDBModel, car_id)
    if response.status_code == 200:
        msg = f"Car (ID={car_id}) has been deleted."
        return _log_info_and_respond(msg)
    else:
        msg = f"Car (ID={car_id}) could not be deleted. {response.body['detail']}"
        return _log_error_and_respond(msg, response.status_code, response.body["title"])


def get_car(car_id: int) -> _Response:
    """Get a car identified by 'car_id'."""
    db_cars = _db_access.get(
        _db_models.CarDBModel,
        criteria={"id": lambda x: x == car_id},
        omitted_relationships=[_db_models.CarDBModel.orders],
    )
    if len(db_cars) == 0:
        return _log_error_and_respond(
            f"Car with ID={car_id} was not found.", 404, title="Object was not found"
        )
    else:
        car = _get_car_with_last_state(db_cars[0])
        _log_info(f"Car with ID={car_id} was found.")
        return _json_response(car)


def get_cars() -> _Response:  # noqa: E501
    """List all cars."""
    db_cars = _db_access.get(
        _db_models.CarDBModel,
        omitted_relationships=[_db_models.CarDBModel.orders],
    )
    cars: list[_models.Car] = list()
    if len(db_cars) == 0:
        _log_info("Listing all cars: no cars found.")
    else:
        for db_car in db_cars:
            car = _get_car_with_last_state(db_car)
            cars.append(car)
        _log_info(f"Listing all cars: {len(cars)} cars found.")
    return _json_response(cars)


def update_cars() -> _Response:
    """Update existing cars.

    If any of the cars' update fails, no cars are updated on the server.

    The car update can succeed only if:
    - the car already exists,
    - the platform HW exists,
    - the default route exists, if it is specified,
    - the car name is unique.
    - the platform HW is not referenced by any other existing car.
    """
    if connexion.request.is_json:
        cars = [_models.Car.from_dict(item) for item in connexion.request.get_json()]  # noqa: E501
        car_db_model = [_obj_to_db.car_to_db_model(c) for c in cars]
        response = _db_access.update(*car_db_model)
        if response.status_code == 200:
            return _log_info_and_respond(
                f"Cars with IDs {[c.id for c in cars]} has been succesfully updated."
            )
        else:
            msg = f"Cars with IDs {[c.id for c in cars]} could not be updated. {response.body['detail']}"
            return _log_error_and_respond(msg, response.status_code, response.body["title"])
    else:
        return _log_invalid_request_body_format()


def _get_car_with_last_state(car_db_model: _db_models.CarDBModel) -> _models.Car:
    db_last_states = _db_access.get(
        _db_models.CarStateDBModel,
        criteria={"car_id": lambda x: x == car_db_model.id},
        sort_result_by={"timestamp": "desc", "id": "desc"},
        first_n=1,
    )
    last_state = _obj_to_db.car_state_from_db_model(db_last_states[0])
    car = _obj_to_db.car_from_db_model(car_db_model, last_state)
    return car


def _post_default_car_state(car_id: int) -> _Response:
    car_state = _models.CarState(
        status=_models.CarStatus.OUT_OF_ORDER, car_id=car_id, fuel=0, speed=0.0
    )
    response = _create_car_state_from_argument_and_post([car_state])
    return response
