import unittest

from flask import json

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.platform_hw_id import Order  # noqa: E501
from fleet_management_api.test import BaseTestCase


class TestPlatformHwIdController(BaseTestCase):
    """PlatformHwIdController integration test stubs"""

    def test_create_hw_id(self):
        """Test case for create_hw_id

        Create a new platform hwId
        """
        platform_hw_id = {"name":"ABCD1234EF56","id":1}
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/platformhwid',
            method='POST',
            headers=headers,
            data=json.dumps(platform_hw_id),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_hw_id(self):
        """Test case for delete_hw_id

        Delete a platform hwId
        """
        headers = {
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/platformhwid/{platformhwid_id}'.format(platformhwid_id=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_hw_id(self):
        """Test case for get_hw_id

        Finds platform hwId by ID
        """
        headers = {
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/platformhwid/{platformhwid_id}'.format(platformhwid_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_hw_ids(self):
        """Test case for get_hw_ids

        Finds all platform hwIds
        """
        headers = {
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/platformhwid',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
