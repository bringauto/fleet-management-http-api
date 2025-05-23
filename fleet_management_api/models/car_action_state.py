from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleet_management_api.models.base_model import Model
from fleet_management_api.models.car_action_status import CarActionStatus
from fleet_management_api import util

from fleet_management_api.models.car_action_status import CarActionStatus  # noqa: E501

class CarActionState(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, car_id=None, timestamp=None, action_status=None):  # noqa: E501
        """CarActionState - a model defined in OpenAPI

        :param id: The id of this CarActionState.  # noqa: E501
        :type id: int
        :param car_id: The car_id of this CarActionState.  # noqa: E501
        :type car_id: int
        :param timestamp: The timestamp of this CarActionState.  # noqa: E501
        :type timestamp: int
        :param action_status: The action_status of this CarActionState.  # noqa: E501
        :type action_status: CarActionStatus
        """
        self.openapi_types = {
            'id': int,
            'car_id': int,
            'timestamp': int,
            'action_status': CarActionStatus
        }

        self.attribute_map = {
            'id': 'id',
            'car_id': 'carId',
            'timestamp': 'timestamp',
            'action_status': 'actionStatus'
        }

        self._id = id
        self._car_id = car_id
        self._timestamp = timestamp
        self._action_status = action_status

    @classmethod
    def from_dict(cls, dikt) -> 'CarActionState':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CarActionState of this CarActionState.  # noqa: E501
        :rtype: CarActionState
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> int:
        """Gets the id of this CarActionState.


        :return: The id of this CarActionState.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """Sets the id of this CarActionState.


        :param id: The id of this CarActionState.
        :type id: int
        """

        self._id = id

    @property
    def car_id(self) -> int:
        """Gets the car_id of this CarActionState.


        :return: The car_id of this CarActionState.
        :rtype: int
        """
        return self._car_id

    @car_id.setter
    def car_id(self, car_id: int):
        """Sets the car_id of this CarActionState.


        :param car_id: The car_id of this CarActionState.
        :type car_id: int
        """
        if car_id is None:
            raise ValueError("Invalid value for `car_id`, must not be `None`")  # noqa: E501

        self._car_id = car_id

    @property
    def timestamp(self) -> int:
        """Gets the timestamp of this CarActionState.

        A Unix timestamp in milliseconds. The timestamp is used to determine the time of creation of an object.  # noqa: E501

        :return: The timestamp of this CarActionState.
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: int):
        """Sets the timestamp of this CarActionState.

        A Unix timestamp in milliseconds. The timestamp is used to determine the time of creation of an object.  # noqa: E501

        :param timestamp: The timestamp of this CarActionState.
        :type timestamp: int
        """

        self._timestamp = timestamp

    @property
    def action_status(self) -> CarActionStatus:
        """Gets the action_status of this CarActionState.


        :return: The action_status of this CarActionState.
        :rtype: CarActionStatus
        """
        return self._action_status

    @action_status.setter
    def action_status(self, action_status: CarActionStatus):
        """Sets the action_status of this CarActionState.


        :param action_status: The action_status of this CarActionState.
        :type action_status: CarActionStatus
        """
        if action_status is None:
            raise ValueError("Invalid value for `action_status`, must not be `None`")  # noqa: E501

        self._action_status = action_status
