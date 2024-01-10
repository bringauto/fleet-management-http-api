import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetman_http_api.models.error import Error  # noqa: E501
from fleetman_http_api.models.route import Route  # noqa: E501
from fleetman_http_api import util


def create_route(route):  # noqa: E501
    """Create a new route

     # noqa: E501

    :param route: New route json
    :type route: dict | bytes

    :rtype: Union[Route, Tuple[Route, int], Tuple[Route, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route = Route.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_route(route_id):  # noqa: E501
    """Delete a route

     # noqa: E501

    :param route_id: ID of route to delete
    :type route_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_route(route_id):  # noqa: E501
    """Finds route by ID

     # noqa: E501

    :param route_id: ID of route to return
    :type route_id: int

    :rtype: Union[Route, Tuple[Route, int], Tuple[Route, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_routes():  # noqa: E501
    """Finds all routes

     # noqa: E501


    :rtype: Union[List[Route], Tuple[List[Route], int], Tuple[List[Route], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_route(route):  # noqa: E501
    """Update an existing route by ID

     # noqa: E501

    :param route: Route update json
    :type route: dict | bytes

    :rtype: Union[Route, Tuple[Route, int], Tuple[Route, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route = Route.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
