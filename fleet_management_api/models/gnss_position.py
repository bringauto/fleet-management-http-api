from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleet_management_api.models.base_model import Model
from fleet_management_api import util


class GNSSPosition(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, latitude=0.0, longitude=0.0, altitude=0.0):  # noqa: E501
        """GNSSPosition - a model defined in OpenAPI

        :param latitude: The latitude of this GNSSPosition.  # noqa: E501
        :type latitude: float
        :param longitude: The longitude of this GNSSPosition.  # noqa: E501
        :type longitude: float
        :param altitude: The altitude of this GNSSPosition.  # noqa: E501
        :type altitude: float
        """
        self.openapi_types = {
            'latitude': float,
            'longitude': float,
            'altitude': float
        }

        self.attribute_map = {
            'latitude': 'latitude',
            'longitude': 'longitude',
            'altitude': 'altitude'
        }

        self._latitude = latitude
        self._longitude = longitude
        self._altitude = altitude

    @classmethod
    def from_dict(cls, dikt) -> 'GNSSPosition':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GNSSPosition of this GNSSPosition.  # noqa: E501
        :rtype: GNSSPosition
        """
        return util.deserialize_model(dikt, cls)

    @property
    def latitude(self) -> float:
        """Gets the latitude of this GNSSPosition.


        :return: The latitude of this GNSSPosition.
        :rtype: float
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: float):
        """Sets the latitude of this GNSSPosition.


        :param latitude: The latitude of this GNSSPosition.
        :type latitude: float
        """

        self._latitude = latitude

    @property
    def longitude(self) -> float:
        """Gets the longitude of this GNSSPosition.


        :return: The longitude of this GNSSPosition.
        :rtype: float
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: float):
        """Sets the longitude of this GNSSPosition.


        :param longitude: The longitude of this GNSSPosition.
        :type longitude: float
        """

        self._longitude = longitude

    @property
    def altitude(self) -> float:
        """Gets the altitude of this GNSSPosition.


        :return: The altitude of this GNSSPosition.
        :rtype: float
        """
        return self._altitude

    @altitude.setter
    def altitude(self, altitude: float):
        """Sets the altitude of this GNSSPosition.


        :param altitude: The altitude of this GNSSPosition.
        :type altitude: float
        """

        self._altitude = altitude
