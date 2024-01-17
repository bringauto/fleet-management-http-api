import connexion
from connexion.lifecycle import ConnexionResponse

from fleet_management_api.models.car_state import CarState


def add_car_state(car_state):  # noqa: E501
    if connexion.request.is_json:
        car_state = CarState.from_dict(connexion.request.get_json())  # noqa: E501
    return ConnexionResponse(content_type="text/plain", status_code=501, body="Not yet implemented.")
