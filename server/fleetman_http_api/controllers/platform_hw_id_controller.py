import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetman_http_api.models.error import Error  # noqa: E501
from fleetman_http_api.models.platform_hw_id import PlatformHwId  # noqa: E501
from fleetman_http_api import util


def create_hw_id(platform_hw_id):  # noqa: E501
    """Create a new platform hwId

     # noqa: E501

    :param platform_hw_id: Platform hardware ID json
    :type platform_hw_id: dict | bytes

    :rtype: Union[PlatformHwId, Tuple[PlatformHwId, int], Tuple[PlatformHwId, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        platform_hw_id = PlatformHwId.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_hw_id(platformhwid_id):  # noqa: E501
    """Delete a platform hwId

     # noqa: E501

    :param platformhwid_id: ID of platform hwId to delete
    :type platformhwid_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_hw_id(platformhwid_id):  # noqa: E501
    """Finds platform hwId by ID

     # noqa: E501

    :param platformhwid_id: ID of platform hwId to return
    :type platformhwid_id: int

    :rtype: Union[PlatformHwId, Tuple[PlatformHwId, int], Tuple[PlatformHwId, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_hw_ids():  # noqa: E501
    """Finds all platform hwIds

     # noqa: E501


    :rtype: Union[List[PlatformHwId], Tuple[List[PlatformHwId], int], Tuple[List[PlatformHwId], int, Dict[str, str]]
    """
    return 'do some magic!'
