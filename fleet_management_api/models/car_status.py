from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleet_management_api.models.base_model import Model
from fleet_management_api import util


class CarStatus(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    IDLE = 'idle'
    CHARGING = 'charging'
    OUT_OF_ORDER = 'out_of_order'
    DRIVING = 'driving'
    IN_STOP = 'in_stop'
    PAUSED_BY_PHONE = 'paused_by_phone'
    PAUSED_BY_OBSTACLE = 'paused_by_obstacle'
    PAUSED_BY_BUTTON = 'paused_by_button'
    def __init__(self):  # noqa: E501
        """CarStatus - a model defined in OpenAPI

        """
        self.openapi_types = {
        }

        self.attribute_map = {
        }

    @classmethod
    def from_dict(cls, dikt) -> 'CarStatus':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CarStatus of this CarStatus.  # noqa: E501
        :rtype: CarStatus
        """
        return util.deserialize_model(dikt, cls)
