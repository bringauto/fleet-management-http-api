import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.platform_hw import PlatformHW  # noqa: E501
from fleet_management_api import util


def create_hw(platform_hw):  # noqa: E501
    """Create a new platform HW.

     # noqa: E501

    :param platform_hw: Platform hardware JSON.
    :type platform_hw: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        platform_hw = PlatformHW.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_hw(platform_hw_id):  # noqa: E501
    """Delete a platform HW.

     # noqa: E501

    :param platform_hw_id: ID of platform HW to delete.
    :type platform_hw_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_hw(platform_hw_id):  # noqa: E501
    """Find platform HW by ID.

     # noqa: E501

    :param platform_hw_id: ID of platform HW to return.
    :type platform_hw_id: int

    :rtype: Union[PlatformHW, Tuple[PlatformHW, int], Tuple[PlatformHW, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_hws():  # noqa: E501
    """Finds all platform HW.

     # noqa: E501


    :rtype: Union[List[PlatformHW], Tuple[List[PlatformHW], int], Tuple[List[PlatformHW], int, Dict[str, str]]
    """
    return 'do some magic!'
