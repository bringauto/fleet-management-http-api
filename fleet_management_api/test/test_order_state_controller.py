import unittest

from flask import json

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.order_state import OrderState  # noqa: E501
from fleet_management_api.test import BaseTestCase


class TestOrderStateController(BaseTestCase):
    """OrderStateController integration test stubs"""

    def test_create_order_state(self):
        """Test case for create_order_state

        Create a new order state
        """
        order_state = {"orderId":1,"id":1,"status":"to_accept"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/orderstate',
            method='POST',
            headers=headers,
            data=json.dumps(order_state),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_order_states(self):
        """Test case for get_all_order_states

        Finds all order states
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/orderstate',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_order_states(self):
        """Test case for get_order_states

        Finds order state by ID
        """
        query_string = [('allAvailable', true)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/orderstate/{order_id}'.format(order_id=1),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
