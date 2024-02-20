import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.car_state import CarState  # noqa: E501
from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api import util


def add_car_state(car_state):  # noqa: E501
    """Add a new Car State.

     # noqa: E501

    :param car_state: Car State model in JSON format.
    :type car_state: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car_state = CarState.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_all_car_states():  # noqa: E501
    """Find one or all Car States for a Car with the specified ID.

     # noqa: E501


    :rtype: Union[List[CarState], Tuple[List[CarState], int], Tuple[List[CarState], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_car_states(car_id, all_available=None):  # noqa: E501
    """Find one or all Car States for a given Car.

     # noqa: E501

    :param car_id: ID of the Car for which to find the Car States.
    :type car_id: int
    :param all_available: Whether to return all available car states or only the latest one
    :type all_available: bool

    :rtype: Union[CarState, Tuple[CarState, int], Tuple[CarState, int, Dict[str, str]]
    """
    return 'do some magic!'
