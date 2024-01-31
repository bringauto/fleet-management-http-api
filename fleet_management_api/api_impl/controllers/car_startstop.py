from connexion.lifecycle import ConnexionResponse as _Response # type: ignore

import fleet_management_api.api_impl as _api
import fleet_management_api.models as _models
import fleet_management_api.database.db_access as _db_access
import fleet_management_api.database.db_models as _db_models


def startstop_car(car_id):  # noqa: E501
    cars_db_models = _db_access.get(_db_models.CarDBModel, criteria={'id': lambda x: x==car_id})
    if cars_db_models:
        car = _api.car_from_db_model(cars_db_models[0])
        response = _start_or_stop_car(car)
        return response
    else:
        return _Response(
            status_code=404, body = f"Car (id={car_id}) not found.", content_type='text/plain'
        )


def _start_or_stop_car(car: _models.Car) -> _Response:
    return _api.log_and_respond(501, "Functionality of starting/stoppin car has not been implemented yet.")