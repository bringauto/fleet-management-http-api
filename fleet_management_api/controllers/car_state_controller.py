import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.car_state import CarState  # noqa: E501
from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api import util


def create_car_states(car_state):  # noqa: E501
    """Add new Car States.

     # noqa: E501

    :param car_state: A list of Car State model in JSON format.
    :type car_state: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car_state = [CarState.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def get_all_car_states(wait=None, since=None, last_n=None):  # noqa: E501
    """Find one or all Car States for all existing Cars.

     # noqa: E501

    :param wait: Applies to GET methods when no objects would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next object to be created and then returns it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only objects created at the time or later will be returned. If unspecified, all objects are returned (since is set to 0 in that case).
    :type since: int
    :param last_n: If specified, only the last N objects will be returned. If unspecified, all objects are returned. \\ If some states have identical timestamps and they all do not fit into the maximum N states, only those with higher IDs are returned. If value smaller than 1 is provided, this filtering is ignored.
    :type last_n: int

    :rtype: Union[List[CarState], Tuple[List[CarState], int], Tuple[List[CarState], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_car_states(car_id, wait=None, since=None, last_n=None):  # noqa: E501
    """Find one or all Car States for a Car with given ID.

     # noqa: E501

    :param car_id: The car ID.
    :type car_id: int
    :param wait: Applies to GET methods when no objects would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next object to be created and then returns it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only objects created at the time or later will be returned. If unspecified, all objects are returned (since is set to 0 in that case).
    :type since: int
    :param last_n: If specified, only the last N objects will be returned. If unspecified, all objects are returned. \\ If some states have identical timestamps and they all do not fit into the maximum N states, only those with higher IDs are returned. If value smaller than 1 is provided, this filtering is ignored.
    :type last_n: int

    :rtype: Union[List[CarState], Tuple[List[CarState], int], Tuple[List[CarState], int, Dict[str, str]]
    """
    return 'do some magic!'
