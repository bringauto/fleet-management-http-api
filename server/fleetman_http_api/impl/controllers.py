import sys
sys.path.append('./server')
from typing import Tuple, List, Dict

import connexion

from fleetman_http_api.models import Car


def create_car(car: Dict|Car) -> Tuple[str, int]:  # noqa: E501
    """Create a new car

     # noqa: E501

    :param car: New car json
    :type car: dict | bytes

    :rtype: Union[Car, Tuple[Car, int], Tuple[Car, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car = Car.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_cars() -> Tuple[List[Car], int]:  # noqa: E501
    """Finds all cars

     # noqa: E501

    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    return [], 200



