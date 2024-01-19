import unittest

from flask import json

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.stop import Stop  # noqa: E501
from fleet_management_api.test import BaseTestCase


class TestStopController(BaseTestCase):
    """StopController integration test stubs"""

    def test_create_stop(self):
        """Test case for create_stop

        Create a new stop
        """
        stop = {"name":"Lidická","id":1,"position":{"altitude":400.25,"latitude":49.204117,"longitude":16.606525},"notification_phone":{"phone":"+420123456789"}}
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
        stop = {"name":"Lidická","id":1,"position":{"altitude":400.25,"latitude":49.204117,"longitude":16.606525},"notification_phone":{"phone":"+420123456789"}}
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
