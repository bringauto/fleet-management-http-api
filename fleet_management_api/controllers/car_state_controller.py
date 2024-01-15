import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.car_state import CarState  # noqa: E501
from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api import util


def add_car_state(car_state):  # noqa: E501
    """Add a new state for a car by ID

     # noqa: E501

    :param car_state: Car state json
    :type car_state: dict | bytes

    :rtype: Union[CarState, Tuple[CarState, int], Tuple[CarState, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car_state = CarState.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
