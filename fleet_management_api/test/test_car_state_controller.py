import unittest

from flask import json

from fleet_management_api.models.car_state import CarState  # noqa: E501
from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.test import BaseTestCase


class TestCarStateController(BaseTestCase):
    """CarStateController integration test stubs"""

    def test_add_car_state(self):
        """Test case for add_car_state

        Add a new state for a car by ID
        """
        car_state = {"fuel":80,"id":1,"position":{"altitude":400.25,"latitude":49.204117,"longitude":16.606525},"speed":20.5,"carId":1}
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
