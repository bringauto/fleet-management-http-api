from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleet_management_api.models.base_model import Model
from fleet_management_api.models.mobile_phone import MobilePhone
from fleet_management_api.models.order_status import OrderStatus
from fleet_management_api.models.priority import Priority
from fleet_management_api import util

from fleet_management_api.models.mobile_phone import MobilePhone  # noqa: E501
from fleet_management_api.models.order_status import OrderStatus  # noqa: E501
from fleet_management_api.models.priority import Priority  # noqa: E501

class Order(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, priority=None, user_id=None, status=None, car_id=None, target_stop_id=None, stop_route_id=None, notification_phone=None):  # noqa: E501
        """Order - a model defined in OpenAPI

        :param id: The id of this Order.  # noqa: E501
        :type id: int
        :param priority: The priority of this Order.  # noqa: E501
        :type priority: Priority
        :param user_id: The user_id of this Order.  # noqa: E501
        :type user_id: int
        :param status: The status of this Order.  # noqa: E501
        :type status: OrderStatus
        :param car_id: The car_id of this Order.  # noqa: E501
        :type car_id: int
        :param target_stop_id: The target_stop_id of this Order.  # noqa: E501
        :type target_stop_id: int
        :param stop_route_id: The stop_route_id of this Order.  # noqa: E501
        :type stop_route_id: int
        :param notification_phone: The notification_phone of this Order.  # noqa: E501
        :type notification_phone: MobilePhone
        """
        self.openapi_types = {
            'id': int,
            'priority': Priority,
            'user_id': int,
            'status': OrderStatus,
            'car_id': int,
            'target_stop_id': int,
            'stop_route_id': int,
            'notification_phone': MobilePhone
        }

        self.attribute_map = {
            'id': 'id',
            'priority': 'priority',
            'user_id': 'userId',
            'status': 'status',
            'car_id': 'carId',
            'target_stop_id': 'targetStopId',
            'stop_route_id': 'stopRouteId',
            'notification_phone': 'notificationPhone'
        }

        self._id = id
        self._priority = priority
        self._user_id = user_id
        self._status = status
        self._car_id = car_id
        self._target_stop_id = target_stop_id
        self._stop_route_id = stop_route_id
        self._notification_phone = notification_phone

    @classmethod
    def from_dict(cls, dikt) -> 'Order':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Order of this Order.  # noqa: E501
        :rtype: Order
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> int:
        """Gets the id of this Order.


        :return: The id of this Order.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """Sets the id of this Order.


        :param id: The id of this Order.
        :type id: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def priority(self) -> Priority:
        """Gets the priority of this Order.


        :return: The priority of this Order.
        :rtype: Priority
        """
        return self._priority

    @priority.setter
    def priority(self, priority: Priority):
        """Sets the priority of this Order.


        :param priority: The priority of this Order.
        :type priority: Priority
        """

        self._priority = priority

    @property
    def user_id(self) -> int:
        """Gets the user_id of this Order.


        :return: The user_id of this Order.
        :rtype: int
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        """Sets the user_id of this Order.


        :param user_id: The user_id of this Order.
        :type user_id: int
        """
        if user_id is None:
            raise ValueError("Invalid value for `user_id`, must not be `None`")  # noqa: E501

        self._user_id = user_id

    @property
    def status(self) -> OrderStatus:
        """Gets the status of this Order.


        :return: The status of this Order.
        :rtype: OrderStatus
        """
        return self._status

    @status.setter
    def status(self, status: OrderStatus):
        """Sets the status of this Order.


        :param status: The status of this Order.
        :type status: OrderStatus
        """

        self._status = status

    @property
    def car_id(self) -> int:
        """Gets the car_id of this Order.


        :return: The car_id of this Order.
        :rtype: int
        """
        return self._car_id

    @car_id.setter
    def car_id(self, car_id: int):
        """Sets the car_id of this Order.


        :param car_id: The car_id of this Order.
        :type car_id: int
        """
        if car_id is None:
            raise ValueError("Invalid value for `car_id`, must not be `None`")  # noqa: E501

        self._car_id = car_id

    @property
    def target_stop_id(self) -> int:
        """Gets the target_stop_id of this Order.


        :return: The target_stop_id of this Order.
        :rtype: int
        """
        return self._target_stop_id

    @target_stop_id.setter
    def target_stop_id(self, target_stop_id: int):
        """Sets the target_stop_id of this Order.


        :param target_stop_id: The target_stop_id of this Order.
        :type target_stop_id: int
        """
        if target_stop_id is None:
            raise ValueError("Invalid value for `target_stop_id`, must not be `None`")  # noqa: E501

        self._target_stop_id = target_stop_id

    @property
    def stop_route_id(self) -> int:
        """Gets the stop_route_id of this Order.


        :return: The stop_route_id of this Order.
        :rtype: int
        """
        return self._stop_route_id

    @stop_route_id.setter
    def stop_route_id(self, stop_route_id: int):
        """Sets the stop_route_id of this Order.


        :param stop_route_id: The stop_route_id of this Order.
        :type stop_route_id: int
        """
        if stop_route_id is None:
            raise ValueError("Invalid value for `stop_route_id`, must not be `None`")  # noqa: E501

        self._stop_route_id = stop_route_id

    @property
    def notification_phone(self) -> MobilePhone:
        """Gets the notification_phone of this Order.


        :return: The notification_phone of this Order.
        :rtype: MobilePhone
        """
        return self._notification_phone

    @notification_phone.setter
    def notification_phone(self, notification_phone: MobilePhone):
        """Sets the notification_phone of this Order.


        :param notification_phone: The notification_phone of this Order.
        :type notification_phone: MobilePhone
        """

        self._notification_phone = notification_phone
