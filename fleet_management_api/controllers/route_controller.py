import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.route import Route  # noqa: E501
from fleet_management_api.models.route_visualization import RouteVisualization  # noqa: E501
from fleet_management_api import util


def create_routes(route, tenant=None):  # noqa: E501
    """Create new Routes.

     # noqa: E501

    :param route: A list of Route models in JSON format.
    :type route: list | bytes
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[List[Route], Tuple[List[Route], int], Tuple[List[Route], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route = [Route.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def delete_route(route_id, tenant=None):  # noqa: E501
    """Delete a Route with the specified ID.

     # noqa: E501

    :param route_id: An ID a the Route
    :type route_id: int
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_route(route_id, tenant=None):  # noqa: E501
    """Find a single Route with the specified ID.

     # noqa: E501

    :param route_id: An ID a the Route
    :type route_id: int
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[Route, Tuple[Route, int], Tuple[Route, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_route_visualization(route_id, tenant=None):  # noqa: E501
    """Find Route Visualization for a Route identified by the route&#39;s ID.

     # noqa: E501

    :param route_id: An ID a the Route
    :type route_id: int
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[RouteVisualization, Tuple[RouteVisualization, int], Tuple[RouteVisualization, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_routes(tenant=None):  # noqa: E501
    """Find and return all existing Routes.

     # noqa: E501

    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[List[Route], Tuple[List[Route], int], Tuple[List[Route], int, Dict[str, str]]
    """
    return 'do some magic!'


def redefine_route_visualizations(route_visualization, tenant=None):  # noqa: E501
    """Redefine Route Visualizations for existing Routes.

     # noqa: E501

    :param route_visualization: A list of Route Visualization models in JSON format.
    :type route_visualization: list | bytes
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[List[RouteVisualization], Tuple[List[RouteVisualization], int], Tuple[List[RouteVisualization], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route_visualization = [RouteVisualization.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def update_routes(route, tenant=None):  # noqa: E501
    """Update already existing Routes.

     # noqa: E501

    :param route: JSON representation of a list of the Routes with updated data.
    :type route: list | bytes
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        route = [Route.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'
