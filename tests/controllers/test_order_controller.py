import unittest

import fleet_management_api.database.connection as connection
from fleet_management_api.models import Order, Car, MobilePhone
from fleet_management_api.app import get_app


class Test_Sending_And_Retrieving_Order(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_connection_source()
        self.app = get_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car.to_dict())

    def test_sending_order_to_exising_car(self):
        order_id = 78
        order = Order(
            id=order_id,
            user_id=789,
            car_id=12,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        with self.app.test_client() as c:
            response = c.post('/v1/order', json=order.to_dict())
            self.assertEqual(response.status_code, 200)

    def test_sending_order_to_non_exising_car_yields_code_404(self):
        order_id = 78
        nonexistent_car_id = 6546515
        order = Order(
            id=order_id,
            user_id=789,
            car_id=nonexistent_car_id,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        with self.app.test_client() as c:
            response = c.post('/v1/order', json=order.to_dict())
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_order_data_yields_code_400(self):
        incomplete_order_dict = {}
        with self.app.test_client() as c:
            response = c.post('/v1/order', json=incomplete_order_dict)
            self.assertEqual(response.status_code, 400)

    def test_repeated_sending_of_order_with_identical_id_yields_code_400(self):
        order_id = 78
        order = Order(
            id=order_id,
            user_id=789,
            car_id=12,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        with self.app.test_client() as c:
            response = c.post('/v1/order', json=order.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/order', json=order.to_dict())
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main() # pragma: no coverage