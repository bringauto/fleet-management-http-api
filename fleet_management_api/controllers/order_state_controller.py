import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.order_state import OrderState  # noqa: E501
from fleet_management_api import util


def create_order_state(order_state):  # noqa: E501
    """Create a new order state

     # noqa: E501

    :param order_state: New order state json
    :type order_state: dict | bytes

    :rtype: Union[OrderState, Tuple[OrderState, int], Tuple[OrderState, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        order_state = OrderState.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_all_order_states():  # noqa: E501
    """Finds all order states

     # noqa: E501


    :rtype: Union[List[OrderState], Tuple[List[OrderState], int], Tuple[List[OrderState], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order_states(order_id, all_available=None):  # noqa: E501
    """Finds order state by ID

     # noqa: E501

    :param order_id: ID of order for which states shall be returned
    :type order_id: int
    :param all_available: Whether to return all available order states or only the latest one
    :type all_available: bool

    :rtype: Union[OrderState, Tuple[OrderState, int], Tuple[OrderState, int, Dict[str, str]]
    """
    return 'do some magic!'
