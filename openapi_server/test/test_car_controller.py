import unittest

from flask import json

from openapi_server.models.car import Car  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.test import BaseTestCase


class TestCarController(BaseTestCase):
    """CarController integration test stubs"""

    def test_create_car(self):
        """Test case for create_car

        Create a new car
        """
        car = {"underTest":True,"name":"name","defaultRouteId":1,"id":0,"platformId":6,"carAdminPhone":{"phone":"phone"}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/car',
            method='POST',
            headers=headers,
            data=json.dumps(car),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_car(self):
        """Test case for delete_car

        Delete a car
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/car/{car_id}'.format(car_id=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_car(self):
        """Test case for get_car

        Finds car by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/car/{car_id}'.format(car_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cars(self):
        """Test case for get_cars

        Finds all cars
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/car',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_startstop_car(self):
        """Test case for startstop_car

        Start/stop car by ID (intended for phonecalls)
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/car/startstop/{car_id}'.format(car_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_car(self):
        """Test case for update_car

        Update an existing car by ID
        """
        car = {"underTest":True,"name":"name","defaultRouteId":1,"id":0,"platformId":6,"carAdminPhone":{"phone":"phone"}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/car',
            method='PUT',
            headers=headers,
            data=json.dumps(car),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
