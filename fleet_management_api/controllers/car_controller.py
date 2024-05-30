import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.car import Car  # noqa: E501
from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api import util


def create_cars(car):  # noqa: E501
    """Create new Car objects.

     # noqa: E501

    :param car: A list of Car models in JSON format.
    :type car: list | bytes

    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car = [Car.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def delete_car(car_id):  # noqa: E501
    """Delete a Car identified by its ID.

     # noqa: E501

    :param car_id: The ID of the Car to be deleted.
    :type car_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_car(car_id):  # noqa: E501
    """Find a single Car by its ID.

     # noqa: E501

    :param car_id: An ID of the Car to be returned.
    :type car_id: int

    :rtype: Union[Car, Tuple[Car, int], Tuple[Car, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_cars():  # noqa: E501
    """Find and return all existing Cars.

     # noqa: E501


    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_cars():  # noqa: E501
    """Update already existing Cars.

     # noqa: E501

    :param car: JSON representation of a list of the Cars with updated data.
    :type car: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car = [Car.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'
