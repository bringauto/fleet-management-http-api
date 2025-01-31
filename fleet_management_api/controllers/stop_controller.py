import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.stop import Stop  # noqa: E501
from fleet_management_api import util


def create_stops(stop):  # noqa: E501
    """Create new Stops.

     # noqa: E501

    :param stop: A list of Stop models in JSON format.
    :type stop: list | bytes

    :rtype: Union[List[Stop], Tuple[List[Stop], int], Tuple[List[Stop], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        stop = [Stop.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def delete_stop(stop_id):  # noqa: E501
    """Delete a Stop with the specified ID.

     # noqa: E501

    :param stop_id: The Stop ID.
    :type stop_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_stop(stop_id):  # noqa: E501
    """Find and return a single Stop by its ID.

     # noqa: E501

    :param stop_id: The Stop ID.
    :type stop_id: int

    :rtype: Union[Stop, Tuple[Stop, int], Tuple[Stop, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_stops():  # noqa: E501
    """Find and return all existing Stops.

     # noqa: E501


    :rtype: Union[List[Stop], Tuple[List[Stop], int], Tuple[List[Stop], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_stops(stop):  # noqa: E501
    """Update already existing Stops.

     # noqa: E501

    :param stop: JSON representation of a list of the Stops with updated data.
    :type stop: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        stop = [Stop.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'
