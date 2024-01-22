from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleet_management_api.models.base_model import Model
from fleet_management_api import util


class OrderStatus(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    TO_ACCEPT = 'to_accept'
    ACCEPTED = 'accepted'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELED = 'canceled'
    def __init__(self):  # noqa: E501
        """OrderStatus - a model defined in OpenAPI

        """
        self.openapi_types = {
        }

        self.attribute_map = {
        }

    @classmethod
    def from_dict(cls, dikt) -> 'OrderStatus':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The OrderStatus of this OrderStatus.  # noqa: E501
        :rtype: OrderStatus
        """
        return util.deserialize_model(dikt, cls)