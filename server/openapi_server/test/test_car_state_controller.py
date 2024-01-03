import unittest

from flask import json

from openapi_server.models.car_state import CarState  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.test import BaseTestCase


class TestCarStateController(BaseTestCase):
    """CarStateController integration test stubs"""

    def test_add_car_state(self):
        """Test case for add_car_state

        Add a new state for a car by ID
        """
        car_state = {"fuel":6,"id":0,"position":{"altitude":7.0614014,"latitude":5.637377,"longitude":2.302136},"speed":5.962134,"carId":1}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/carstate',
            method='POST',
            headers=headers,
            data=json.dumps(car_state),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
