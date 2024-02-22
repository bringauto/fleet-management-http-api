import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.route import Route  # noqa: E501
from fleet_management_api.models.route_visualization import RouteVisualization  # noqa: E501
from fleet_management_api import util


def create_route(route):  # noqa: E501
    """Create a new Route.

     # noqa: E501

    :param route: Route model in JSON format.
    :type route: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route = Route.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_route(route_id):  # noqa: E501
    """Delete a Route with the specified ID.

     # noqa: E501

    :param route_id: An ID a the Route
    :type route_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_route(route_id):  # noqa: E501
    """Find a single Route with the specified ID.

     # noqa: E501

    :param route_id: An ID a the Route
    :type route_id: int

    :rtype: Union[Route, Tuple[Route, int], Tuple[Route, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_route_visualization(route_id):  # noqa: E501
    """Find Route Visualization for a Route identified by the route&#39;s ID.

     # noqa: E501

    :param route_id: An ID a the Route
    :type route_id: int

    :rtype: Union[RouteVisualization, Tuple[RouteVisualization, int], Tuple[RouteVisualization, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_routes():  # noqa: E501
    """Find and return all existing Routes.

     # noqa: E501


    :rtype: Union[List[Route], Tuple[List[Route], int], Tuple[List[Route], int, Dict[str, str]]
    """
    return 'do some magic!'


def redefine_route_visualization(route_visualization):  # noqa: E501
    """Redefine Route Visualization for an existing Route.

     # noqa: E501

    :param route_visualization: Route Visualization model in JSON format.
    :type route_visualization: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route_visualization = RouteVisualization.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def update_route(route):  # noqa: E501
    """Update already existing Route.

     # noqa: E501

    :param route: JSON representation of the updated Route.
    :type route: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route = Route.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
