import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.order import Order  # noqa: E501
from fleet_management_api import util


def create_orders(order):  # noqa: E501
    """Create new Orders.

     # noqa: E501

    :param order: A list of Order models in JSON format.
    :type order: list | bytes

    :rtype: Union[List[Order], Tuple[List[Order], int], Tuple[List[Order], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        order = [Order.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def delete_order(car_id, order_id):  # noqa: E501
    """Delete an Order identified by its ID and ID of a car to which it is assigned.

     # noqa: E501

    :param car_id: ID of the Car to which the Order is assigned.
    :type car_id: int
    :param order_id: ID of the Order to be returned.
    :type order_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_car_orders(car_id, since=None):  # noqa: E501
    """Find existing Orders by the corresponding Car ID and return them.

     # noqa: E501

    :param car_id: ID of the Car for which Orders shall be returned.
    :type car_id: int
    :param since: A Unix timestamp in milliseconds. If specified, only objects created at the time or later will be returned. If unspecified, all objects are returned (since is set to 0 in that case).
    :type since: int

    :rtype: Union[List[Order], Tuple[List[Order], int], Tuple[List[Order], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order(car_id, order_id):  # noqa: E501
    """Find an existing Order by the car ID and the order ID and return it.

     # noqa: E501

    :param car_id: ID of the Car to which the Order is assigned.
    :type car_id: int
    :param order_id: ID of the Order to be returned.
    :type order_id: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_orders(since=None):  # noqa: E501
    """Find all currently existing Orders.

     # noqa: E501

    :param since: A Unix timestamp in milliseconds. If specified, only objects created at the time or later will be returned. If unspecified, all objects are returned (since is set to 0 in that case).
    :type since: int

    :rtype: Union[List[Order], Tuple[List[Order], int], Tuple[List[Order], int, Dict[str, str]]
    """
    return 'do some magic!'
