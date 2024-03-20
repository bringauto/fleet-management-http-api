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


def delete_order(order_id):  # noqa: E501
    """Delete an Order with the specified ID.

     # noqa: E501

    :param order_id: ID of the Order to be deleted.
    :type order_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order(order_id):  # noqa: E501
    """Find an existing Order by its ID and return it.

     # noqa: E501

    :param order_id: ID of the Order to be returned.
    :type order_id: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_orders():  # noqa: E501
    """Find all currently existing Orders.

     # noqa: E501


    :rtype: Union[List[Order], Tuple[List[Order], int], Tuple[List[Order], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_updated_orders(car_id):  # noqa: E501
    """Get updated Orders for a given Car specified by its ID.

     # noqa: E501

    :param car_id: ID of the Car for which updated Orders are requested.
    :type car_id: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'
