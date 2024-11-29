import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.car_action_state import CarActionState  # noqa: E501
from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api import util


def get_car_action_states():  # noqa: E501
    """Finds car action states for a Car with given carId.

     # noqa: E501


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
