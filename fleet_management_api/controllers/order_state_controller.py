import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.order_state import OrderState  # noqa: E501
from fleet_management_api import util


def create_order_states(order_state):  # noqa: E501
    """Add a new Order State.

     # noqa: E501

    :param order_state: Order State model in JSON format.
    :type order_state: list | bytes

    :rtype: Union[OrderState, Tuple[OrderState, int], Tuple[OrderState, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        order_state = [OrderState.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def get_all_order_states(wait=None, since=None, last_n=None, car_id=None):  # noqa: E501
    """Find Order States for all existing Orders.

     # noqa: E501

    :param wait: Applies to GET methods when no objects would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next object to be created and then returns it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only objects created at the time or later will be returned. If unspecified, all objects are returned (since is set to 0 in that case).
    :type since: int
    :param last_n: If specified, only the last N objects will be returned. If unspecified, all objects are returned. \\ If some states have identical timestamps and they all do not fit into the maximum N states, only those with higher IDs are returned. If value smaller than 1 is provided, this filtering is ignored.
    :type last_n: int
    :param car_id: An optional parameter for filtering only objects related to a car with the specified ID.
    :type car_id: int

    :rtype: Union[List[OrderState], Tuple[List[OrderState], int], Tuple[List[OrderState], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order_states(order_id, wait=None, since=None, last_n=None):  # noqa: E501
    """Find all Order States for a particular Order specified by its ID.

     # noqa: E501

    :param order_id: ID of the Order for which to find the Order States.
    :type order_id: int
    :param wait: Applies to GET methods when no objects would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next object to be created and then returns it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only objects created at the time or later will be returned. If unspecified, all objects are returned (since is set to 0 in that case).
    :type since: int
    :param last_n: If specified, only the last N objects will be returned. If unspecified, all objects are returned. \\ If some states have identical timestamps and they all do not fit into the maximum N states, only those with higher IDs are returned. If value smaller than 1 is provided, this filtering is ignored.
    :type last_n: int

    :rtype: Union[List[OrderState], Tuple[List[OrderState], int], Tuple[List[OrderState], int, Dict[str, str]]
    """
    return 'do some magic!'
