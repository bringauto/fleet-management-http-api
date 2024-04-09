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


def get_all_car_states(wait=None, since=None):  # noqa: E501
    """Find one or all Car States for all existing Cars.

     # noqa: E501

    :param wait: Applies to GET methods when no order statuses would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next order state to be created and then return it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only states created at the time or later will be returned. If unspecified, all states are returned (since is set to 0 in that case).
    :type since: int

    :rtype: Union[List[CarState], Tuple[List[CarState], int], Tuple[List[CarState], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_car_states(car_id, wait=None, since=None, all_available=None):  # noqa: E501
    """Find one or all Car States for a Car with given ID.

     # noqa: E501

    :param car_id: ID of the Car for which to find the Car States.
    :type car_id: int
    :param wait: Applies to GET methods when no order statuses would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next order state to be created and then return it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only states created at the time or later will be returned. If unspecified, all states are returned (since is set to 0 in that case).
    :type since: int
    :param all_available: Whether to return all available car states or only the latest one
    :type all_available: bool

    :rtype: Union[List[CarState], Tuple[List[CarState], int], Tuple[List[CarState], int, Dict[str, str]]
    """
    return 'do some magic!'
