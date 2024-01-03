import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.car import Car  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server import util


def create_car(car):  # noqa: E501
    """Create a new car

     # noqa: E501

    :param car: New car json
    :type car: dict | bytes

    :rtype: Union[Car, Tuple[Car, int], Tuple[Car, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car = Car.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_car(car_id:int):  # noqa: E501
    """Delete a car

     # noqa: E501

    :param car_id: ID of car to delete
    :type car_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_car(car_id:int):  # noqa: E501
    """Finds car by ID

     # noqa: E501

    :param car_id: ID of car to return
    :type car_id: int

    :rtype: Union[Car, Tuple[Car, int], Tuple[Car, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_cars():  # noqa: E501
    """Finds all cars

     # noqa: E501


    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    return 'do some magic!'


def startstop_car(car_id:int):  # noqa: E501
    """Start/stop car by ID (intended for phonecalls)

     # noqa: E501

    :param car_id: ID of car to start/stop
    :type car_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def update_car(car:int):  # noqa: E501
    """Update an existing car by ID

     # noqa: E501

    :param car: Car update json
    :type car: dict | bytes

    :rtype: Union[Car, Tuple[Car, int], Tuple[Car, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car = Car.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
