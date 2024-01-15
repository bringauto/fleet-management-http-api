import unittest

from flask import json

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.route import Route  # noqa: E501
from fleet_management_api.test import BaseTestCase


class TestRouteController(BaseTestCase):
    """RouteController integration test stubs"""

    def test_create_route(self):
        """Test case for create_route

        Create a new route
        """
        route = {"name":"Lužánky","stopIds":[1,2,3,4],"id":1,"points":[{"latitude":49.204117,"longitude":16.606525,"altitude":400.25}]}
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
        route = {"name":"Lužánky","stopIds":[1,2,3,4],"id":1,"points":[{"latitude":49.204117,"longitude":16.606525,"altitude":400.25}]}
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
