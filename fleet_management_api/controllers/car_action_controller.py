import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.car_action_state import CarActionState  # noqa: E501
from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api import util


def get_car_action_states(car_id, wait=None, since=None, last_n=None):  # noqa: E501
    """Finds car action states for a Car with given carId.

     # noqa: E501

    :param car_id: ID of the Car which should be unpaused.
    :type car_id: int
    :param wait: Applies to GET methods when no objects would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next object to be created and then returns it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only objects created at the time or later will be returned. If unspecified, all objects are returned (since is set to 0 in that case).
    :type since: int
    :param last_n: If specified, only the last N objects will be returned. If unspecified, all objects are returned. \\ If some states have identical timestamps and they all do not fit into the maximum N states, only those with higher IDs are returned. If value smaller than 1 is provided, this filtering is ignored.
    :type last_n: int

    :rtype: Union[List[CarActionState], Tuple[List[CarActionState], int], Tuple[List[CarActionState], int, Dict[str, str]]
    """
    return 'do some magic!'


def pause_car(car_id):  # noqa: E501
    """Finds and pauses a Car with given carId, if not already paused. Sets car action status to PAUSED if it is not in PAUSED action status already.

     # noqa: E501

    :param car_id: ID of the Car which should be paused.
    :type car_id: int

    :rtype: Union[CarActionState, Tuple[CarActionState, int], Tuple[CarActionState, int, Dict[str, str]]
    """
    return 'do some magic!'


def unpause_car(car_id):  # noqa: E501
    """Finds and unpauses a Car with given carId, if paused. Sets car action status to NORMAL only if it is in PAUSED action status.

     # noqa: E501

    :param car_id: ID of the Car which should be unpaused.
    :type car_id: int

    :rtype: Union[CarActionState, Tuple[CarActionState, int], Tuple[CarActionState, int, Dict[str, str]]
    """
    return 'do some magic!'
