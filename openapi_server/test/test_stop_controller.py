import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.stop import Stop  # noqa: E501
from openapi_server.test import BaseTestCase


class TestStopController(BaseTestCase):
    """StopController integration test stubs"""

    def test_create_stop(self):
        """Test case for create_stop

        Create a new stop
        """
        stop = {"notificationPhone":{"phone":"phone"},"name":"name","id":0,"position":{"altitude":7.0614014,"latitude":5.637377,"longitude":2.302136}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/stop',
            method='POST',
            headers=headers,
            data=json.dumps(stop),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_stop(self):
        """Test case for delete_stop

        Delete a stop
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/stop/{stop_id}'.format(stop_id=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_stop(self):
        """Test case for get_stop

        Finds stop by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/stop/{stop_id}'.format(stop_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_stops(self):
        """Test case for get_stops

        Finds all stops
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/stop',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_stop(self):
        """Test case for update_stop

        Update an existing stop by ID
        """
        stop = {"notificationPhone":{"phone":"phone"},"name":"name","id":0,"position":{"altitude":7.0614014,"latitude":5.637377,"longitude":2.302136}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/stop',
            method='PUT',
            headers=headers,
            data=json.dumps(stop),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
