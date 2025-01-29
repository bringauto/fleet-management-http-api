import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.platform_hw import PlatformHW  # noqa: E501
from fleet_management_api import util


def create_hws(platform_hw, tenant=None):  # noqa: E501
    """Create new Platform HW objects.

     # noqa: E501

    :param platform_hw: A list of Platform HW models in JSON format.
    :type platform_hw: list | bytes
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[List[PlatformHW], Tuple[List[PlatformHW], int], Tuple[List[PlatformHW], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        platform_hw = [PlatformHW.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def delete_hw(platform_hw_id, tenant=None):  # noqa: E501
    """Delete Platform HW with the given ID.

     # noqa: E501

    :param platform_hw_id: The Platform HW ID.
    :type platform_hw_id: int
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_hw(platform_hw_id, tenant=None):  # noqa: E501
    """Find Platform HW with the given ID.

     # noqa: E501

    :param platform_hw_id: The Platform HW ID.
    :type platform_hw_id: int
    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[PlatformHW, Tuple[PlatformHW, int], Tuple[PlatformHW, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_hws(tenant=None):  # noqa: E501
    """Find and return all existing Platform HW.

     # noqa: E501

    :param tenant: A parameter for reading and writing only the data related to a given tenant.
    :type tenant: str

    :rtype: Union[List[PlatformHW], Tuple[List[PlatformHW], int], Tuple[List[PlatformHW], int, Dict[str, str]]
    """
    return 'do some magic!'
