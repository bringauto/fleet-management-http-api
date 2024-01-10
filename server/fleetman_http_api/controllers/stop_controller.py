import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetman_http_api.models.error import Error  # noqa: E501
from fleetman_http_api.models.stop import Stop  # noqa: E501
from fleetman_http_api import util


def create_stop(stop):  # noqa: E501
    """Create a new stop

     # noqa: E501

    :param stop: New stop json
    :type stop: dict | bytes

    :rtype: Union[Stop, Tuple[Stop, int], Tuple[Stop, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        stop = Stop.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_stop(stop_id):  # noqa: E501
    """Delete a stop

     # noqa: E501

    :param stop_id: ID of stop to delete
    :type stop_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_stop(stop_id):  # noqa: E501
    """Finds stop by ID

     # noqa: E501

    :param stop_id: ID of stop to return
    :type stop_id: int

    :rtype: Union[Stop, Tuple[Stop, int], Tuple[Stop, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_stops():  # noqa: E501
    """Finds all stops

     # noqa: E501


    :rtype: Union[List[Stop], Tuple[List[Stop], int], Tuple[List[Stop], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_stop(stop):  # noqa: E501
    """Update an existing stop by ID

     # noqa: E501

    :param stop: Stop update json
    :type stop: dict | bytes

    :rtype: Union[Stop, Tuple[Stop, int], Tuple[Stop, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        stop = Stop.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
