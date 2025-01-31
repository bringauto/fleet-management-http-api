import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.models import (
    CarActionState as _CarActionState,
    CarActionStatus as _CarActionStatus,
    CarState as _CarState,
    CarStatus as _CarStatus,
    Car as _Car,
)
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.api_impl.controllers.car_state import (
    create_car_states_from_argument_and_post as _create_car_state_from_argument_and_post,
)
from fleet_management_api.api_impl.controllers.car_action import (
    create_car_action_states_from_argument_and_save_to_db as _create_car_action_state_from_argument_and_post,
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
from fleet_management_api.response_consts import OBJ_NOT_FOUND as _OBJ_NOT_FOUND
from fleet_management_api.api_impl.load_request import (
    RequestJSON as _RequestJSON,
    RequestEmpty as _RequestEmpty,
)
from fleet_management_api.api_impl.tenants import AccessibleTenants as _AccessibleTenants


def create_cars() -> _Response:  # noqa: E501
    """Create new cars.

    If some of the cars' creation fails, no cars are added to the server.

    The car creation can succeed only if:
    - the platform HW exists,
    - the default route exists, if it is specified,
    - the car name is unique.
    - the platform HW is not referenced by any existing car.
    """
    request = _RequestJSON.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    cars: list[_models.Car] = []
    for car_dict in request.data:
        car_dict["lastState"] = None
        car = _models.Car.from_dict(car_dict)
        cars.append(car)
    car_db_models = []
    checked = []
    for car in cars:
        car_db_models.append(_obj_to_db.car_to_db_model(car))
        checked.append(_db_access.db_object_check(_db_models.PlatformHWDB, id_=car.platform_hw_id))
        checked.append(
            _db_access.db_object_check(
                _db_models.RouteDB,
                id_=car.default_route_id,
                allow_nonexistence=True,
            )
        )

    response = _db_access.add(tenants, *car_db_models, checked=checked)
    if response.status_code == 200:
        posted_db_models: list[_db_models.CarDB] = response.body
        ids: list[int] = []
        for model in posted_db_models:
            assert model.id is not None
            ids.append(model.id)
            _log_info(f"Car (ID={model.id}, name='{model.name}') has been created.")

        car_states = _post_default_car_state(tenants, ids).body
        _post_default_car_action_state(tenants, ids).body

        posted_cars: list[_Car] = []
        for model, state in zip(posted_db_models, car_states):
            posted_car = _obj_to_db.car_from_db_model(model, state)
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
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    response = _db_access.delete(tenants, _db_models.CarDB, car_id)
    if response.status_code == 200:
        msg = f"Car (ID={car_id}) has been deleted."
        return _log_info_and_respond(msg)
    else:
        msg = f"Car (ID={car_id}) could not be deleted. {response.body['detail']}"
        return _log_error_and_respond(msg, response.status_code, response.body["title"])


def get_car(car_id: int) -> _Response:
    """Get a car identified by 'car_id'."""
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    db_cars = _db_access.get(
        tenants,
        _db_models.CarDB,
        criteria={"id": lambda x: x == car_id},
        omitted_relationships=[_db_models.CarDB.orders],
    )
    if len(db_cars) == 0:
        return _log_error_and_respond(
            f"Car with ID={car_id} was not found.", 404, title=_OBJ_NOT_FOUND
        )
    else:
        car = _get_car_with_last_state(tenants, db_cars[0])
        _log_info(f"Car with ID={car_id} was found.")
        return _json_response(car)


def get_cars() -> _Response:  # noqa: E501
    """List all cars."""
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    db_cars = _db_access.get(
        tenants, _db_models.CarDB, omitted_relationships=[_db_models.CarDB.orders]
    )
    cars: list[_models.Car] = list()
    if len(db_cars) == 0:
        _log_info("Listing all cars: no cars found.")
    else:
        for db_car in db_cars:
            car = _get_car_with_last_state(tenants, db_car)
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
    request = _RequestJSON.load()
    if not request:
        return _log_invalid_request_body_format()
    tenants = _AccessibleTenants(request)
    cars = [_models.Car.from_dict(item) for item in request.data]  # noqa: E501
    car_db_model = [_obj_to_db.car_to_db_model(c) for c in cars]
    response = _db_access.update(tenants, *car_db_model)
    car_ids = [c.id for c in cars]
    if response.status_code == 200:
        return _log_info_and_respond(f"Cars with IDs {car_ids} has been succesfully updated.")
    else:
        msg = f"Cars with IDs {car_ids} could not be updated. {response.body['detail']}"
        return _log_error_and_respond(msg, response.status_code, response.body["title"])


def _get_car_with_last_state(
    tenants: _AccessibleTenants, car_db_model: _db_models.CarDB
) -> _models.Car:
    last_state = _get_last_car_state(tenants, car_db_model)
    car = _obj_to_db.car_from_db_model(car_db_model, last_state)
    return car


def _get_last_car_state(
    tenants: _AccessibleTenants, car_db_model: _db_models.CarDB
) -> _CarState | None:
    db_last_states = _db_access.get(
        tenants,
        _db_models.CarStateDB,
        criteria={"car_id": lambda x: x == car_db_model.id},
        sort_result_by={"timestamp": "desc", "id": "desc"},
        first_n=1,
    )
    if db_last_states:
        last_state = _obj_to_db.car_state_from_db_model(db_last_states[0])
    else:
        last_state = None
    return last_state


def _post_default_car_state(tenants: _AccessibleTenants, car_ids: list[int]) -> _Response:
    car_states = [_CarState(car_id=id_, status=_CarStatus.OUT_OF_ORDER) for id_ in car_ids]
    response = _create_car_state_from_argument_and_post(tenants, car_states)
    return response


def _post_default_car_action_state(tenants: _AccessibleTenants, car_ids: list[int]) -> _Response:
    car_action_states = [
        _CarActionState(car_id=id_, action_status=_CarActionStatus.NORMAL) for id_ in car_ids
    ]
    response = _create_car_action_state_from_argument_and_post(tenants, car_action_states)
    return response
