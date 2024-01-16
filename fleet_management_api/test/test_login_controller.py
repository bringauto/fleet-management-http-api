import unittest

from flask import json

from fleet_management_api.test import BaseTestCase


class TestLoginController(BaseTestCase):
    """LoginController integration test stubs"""

    def test_login(self):
        """Test case for login

        
        """
        headers = { 
        }
        response = self.client.open(
            '/v1/login',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_token_get(self):
        """Test case for token_get

        
        """
        query_string = [('state', 'your_state_info'),
                        ('session_state', '167e141d-2f55-4d...'),
                        ('iss', 'http%3A%2F%2Flocalhost%3A8081%2Frealms%2Fmaster'),
                        ('code', '5dea27d2-4b2d-48...')]
        headers = { 
        }
        response = self.client.open(
            '/v1/token_get',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_token_refresh(self):
        """Test case for token_refresh

        
        """
        query_string = [('refresh_token', 'eyJhbGciOiJIUzI1NiIsI...')]
        headers = { 
        }
        response = self.client.open(
            '/v1/token_refresh',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
