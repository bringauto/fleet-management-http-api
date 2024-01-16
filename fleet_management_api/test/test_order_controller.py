import unittest

from flask import json

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.order import Order  # noqa: E501
from fleet_management_api.test import BaseTestCase


class TestOrderController(BaseTestCase):
    """OrderController integration test stubs"""

    def test_create_order(self):
        """Test case for create_order

        Create a new order
        """
        order = {"stopRouteId":1,"notificationPhone":{"phone":"+420123456789"},"targetStopId":1,"id":1,"userId":1,"carId":1}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/order',
            method='POST',
            headers=headers,
            data=json.dumps(order),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_order(self):
        """Test case for delete_order

        Delete an order
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/order/{order_id}'.format(order_id=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_order(self):
        """Test case for get_order

        Finds order by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/order/{order_id}'.format(order_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_order_wait(self):
        """Test case for get_order_wait

        Get order by car ID only if it changed
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/order/wait/{car_id}'.format(car_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_orders(self):
        """Test case for get_orders

        Finds all orders
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/order',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_order(self):
        """Test case for update_order

        Update an existing order by ID
        """
        order = {"stopRouteId":1,"notificationPhone":{"phone":"+420123456789"},"targetStopId":1,"id":1,"userId":1,"carId":1}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v1/order',
            method='PUT',
            headers=headers,
            data=json.dumps(order),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()