import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.route import Route  # noqa: E501
from openapi_server.test import BaseTestCase


class TestRouteController(BaseTestCase):
    """RouteController integration test stubs"""

    def test_create_route(self):
        """Test case for create_route

        Create a new route
        """
        route = {"name":"name","stopIds":[6,6],"id":0,"points":[{"altitude":7.0614014,"latitude":5.637377,"longitude":2.302136},{"altitude":7.0614014,"latitude":5.637377,"longitude":2.302136}]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/route',
            method='POST',
            headers=headers,
            data=json.dumps(route),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_route(self):
        """Test case for delete_route

        Delete a route
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/route/{route_id}'.format(route_id=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_route(self):
        """Test case for get_route

        Finds route by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/route/{route_id}'.format(route_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_routes(self):
        """Test case for get_routes

        Finds all routes
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/route',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_route(self):
        """Test case for update_route

        Update an existing route by ID
        """
        route = {"name":"name","stopIds":[6,6],"id":0,"points":[{"altitude":7.0614014,"latitude":5.637377,"longitude":2.302136},{"altitude":7.0614014,"latitude":5.637377,"longitude":2.302136}]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/route',
            method='PUT',
            headers=headers,
            data=json.dumps(route),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
