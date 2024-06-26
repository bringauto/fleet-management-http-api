from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleet_management_api.models.base_model import Model
from fleet_management_api import util


class Route(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, name=None, stop_ids=[]):  # noqa: E501
        """Route - a model defined in OpenAPI

        :param id: The id of this Route.  # noqa: E501
        :type id: int
        :param name: The name of this Route.  # noqa: E501
        :type name: str
        :param stop_ids: The stop_ids of this Route.  # noqa: E501
        :type stop_ids: List[int]
        """
        self.openapi_types = {
            'id': int,
            'name': str,
            'stop_ids': List[int]
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'stop_ids': 'stopIds'
        }

        self._id = id
        self._name = name
        self._stop_ids = stop_ids

    @classmethod
    def from_dict(cls, dikt) -> 'Route':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Route of this Route.  # noqa: E501
        :rtype: Route
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> int:
        """Gets the id of this Route.


        :return: The id of this Route.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """Sets the id of this Route.


        :param id: The id of this Route.
        :type id: int
        """

        self._id = id

    @property
    def name(self) -> str:
        """Gets the name of this Route.


        :return: The name of this Route.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Route.


        :param name: The name of this Route.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def stop_ids(self) -> List[int]:
        """Gets the stop_ids of this Route.


        :return: The stop_ids of this Route.
        :rtype: List[int]
        """
        return self._stop_ids

    @stop_ids.setter
    def stop_ids(self, stop_ids: List[int]):
        """Sets the stop_ids of this Route.


        :param stop_ids: The stop_ids of this Route.
        :type stop_ids: List[int]
        """

        self._stop_ids = stop_ids
