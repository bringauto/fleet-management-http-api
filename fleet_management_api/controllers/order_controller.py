import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.order import Order  # noqa: E501
from fleet_management_api import util


def create_order(order):  # noqa: E501
    """Create a new Order.

     # noqa: E501

    :param order: Order model in JSON format.
    :type order: dict | bytes

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        order = Order.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_car_orders(car_id, wait=None, since=None):  # noqa: E501
    """Find existing Orders by the corresponding Car ID and return them.

     # noqa: E501

    :param car_id: ID of the Car for which Orders shall be returned.
    :type car_id: int
    :param wait: Applies to GET methods when no order statuses would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next order state to be created and then return it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only states created at the time or later will be returned. If unspecified, all states are returned (since is set to 0 in that case).
    :type since: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order(car_id, order_id, wait=None, since=None):  # noqa: E501
    """Find an existing Order by the car ID and the order ID and return it.

     # noqa: E501

    :param car_id: ID of the Car to which the Order is assigned.
    :type car_id: int
    :param order_id: ID of the Order to be returned.
    :type order_id: int
    :param wait: Applies to GET methods when no order statuses would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next order state to be created and then return it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only states created at the time or later will be returned. If unspecified, all states are returned (since is set to 0 in that case).
    :type since: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_orders(wait=None, since=None):  # noqa: E501
    """Find all currently existing Orders.

     # noqa: E501

    :param wait: Applies to GET methods when no order statuses would be returned at the moment of request. If wait&#x3D;true, \\ the request will wait for the next order state to be created and then return it. If wait&#x3D;False or unspecified, the request will return \\ an empty list.
    :type wait: bool
    :param since: A Unix timestamp in milliseconds. If specified, only states created at the time or later will be returned. If unspecified, all states are returned (since is set to 0 in that case).
    :type since: int

    :rtype: Union[List[Order], Tuple[List[Order], int], Tuple[List[Order], int, Dict[str, str]]
    """
    return 'do some magic!'
