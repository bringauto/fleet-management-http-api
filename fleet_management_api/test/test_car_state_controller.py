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
        car_state = {"fuel":80,"id":1,"position":{"altitude":400.25,"latitude":49.204117,"longitude":16.606525},"speed":20.5,"status":"idle","carId":1}
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

    def test_get_all_car_states(self):
        """Test case for get_all_car_states

        Finds all car states
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/carstate',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_car_states(self):
        """Test case for get_car_states

        Finds car states by ID
        """
        query_string = [('allAvailable', true)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/carstate/{car_id}'.format(car_id=1),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
