import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.order import Order  # noqa: E501
from fleet_management_api import util


def create_order(order):  # noqa: E501
    """Create a new order

     # noqa: E501

    :param order: New order json
    :type order: dict | bytes

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        order = Order.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_order(order_id):  # noqa: E501
    """Delete an order

     # noqa: E501

    :param order_id: ID of order to delete
    :type order_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order(order_id):  # noqa: E501
    """Finds order by ID

     # noqa: E501

    :param order_id: ID of order to return
    :type order_id: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order_wait(car_id):  # noqa: E501
    """Get order by car ID only if it changed

     # noqa: E501

    :param car_id: ID of car with order to return
    :type car_id: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_orders():  # noqa: E501
    """Finds all orders

     # noqa: E501


    :rtype: Union[List[Order], Tuple[List[Order], int], Tuple[List[Order], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_order(order):  # noqa: E501
    """Update an existing order by ID

     # noqa: E501

    :param order: Order update json
    :type order: dict | bytes

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        order = Order.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
