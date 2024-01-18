import unittest

import fleet_management_api.database.connection as connection
from fleet_management_api.models import Order, Car, MobilePhone
from fleet_management_api.app import get_app


class Test_Sending_And_Order(unittest.TestCase):

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


class Test_All_Retrieving_Orders(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_connection_source()
        self.app = get_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car.to_dict())

    def test_retrieving_all_orders_when_no_orders_exist_yields_code_200(self):
        with self.app.test_client() as c:
            response = c.get(f'/v1/order')
            self.assertEqual(response.status_code, 200)
            self.assertListEqual(response.json, [])

    def test_retrieving_all_orders_when_some_orders_exist_yields_code_200(self):
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
            c.post('/v1/order', json=order.to_dict())
            response = c.get(f'/v1/order')
            self.assertEqual(response.status_code, 200)
            self.assertListEqual(response.json, [order.to_dict()])


class Test_Retrieving_Single_Order_From_The_Database(unittest.TestCase):

    def setUp(self):
        connection.set_connection_source()
        self.app = get_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car.to_dict())

    def test_retrieving_existing_order(self):
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
            c.post('/v1/order', json=order.to_dict())
            response = c.get(f'/v1/order/{order_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, order.to_dict())

    def test_retrieving_non_existing_order_yields_code_404(self):
        nonexistent_order_id = 65169861848
        with self.app.test_client() as c:
            response = c.get(f'/v1/order/{nonexistent_order_id}')
            self.assertEqual(response.status_code, 404)


class Test_Updating_Order(unittest.TestCase):

    def setUp(self):
        connection.set_connection_source()
        self.app = get_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car.to_dict())
        self.order = Order(
            id=78,
            user_id=789,
            car_id=12,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )

    def test_updating_existing_order(self):
        with self.app.test_client() as c:
            c.post('/v1/order', json=self.order.to_dict())

            # update order attribute
            self.order.target_stop_id = 1234

            response = c.put('/v1/order', json=self.order.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.get(f'/v1/order/{self.order.id}')
            self.assertEqual(response.json["target_stop_id"], 1234)

    def test_updating_nonexistent_order_yields_code_404(self):
        with self.app.test_client() as c:
            response = c.put('/v1/order', json=self.order.to_dict())
            self.assertEqual(response.status_code, 404)

    def test_updating_order_using_incomplete_data_yields_code_400(self):
        incomplete_order_dict = {}
        with self.app.test_client() as c:
            response = c.post('/v1/order', json=self.order.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.put('/v1/order', json=incomplete_order_dict)
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main() # pragma: no coverage