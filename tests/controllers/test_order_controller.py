import unittest

import fleet_management_api.database.connection as _connection
from fleet_management_api.models import Order, Car, MobilePhone
import fleet_management_api.app as _app


class Test_Sending_And_Order(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car)

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
            response = c.post('/v1/order', json=order)
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
            response = c.post('/v1/order', json=order)
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
            response = c.post('/v1/order', json=order)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/order', json=order)
            self.assertEqual(response.status_code, 400)


class Test_Creating_Order_From_Example_In_Spec(unittest.TestCase):

    def test_creating_order_from_example_in_spec(self):
        _connection.set_connection_source_test()
        app = _app.get_test_app().app
        with app.test_client() as c:
            example = c.get('/v1/openapi.json').json["components"]["schemas"]["Order"]["example"]
            car = Car(id=example["carId"], name="Test Car", platform_id=5)
            c.post('/v1/car', json=car)

            response = c.post('/v1/order', json=example)
            self.assertEqual(response.status_code, 200)


class Test_All_Retrieving_Orders(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car)

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
            c.post('/v1/order', json=order)
            response = c.get(f'/v1/order')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Order.from_dict(response.json[0]), order)


class Test_Retrieving_Single_Order_From_The_Database(unittest.TestCase):

    def setUp(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car)

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
            c.post('/v1/order', json=order)
            response = c.get(f'/v1/order/{order_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Order.from_dict(response.json), order)

    def test_retrieving_non_existing_order_yields_code_404(self):
        nonexistent_order_id = 65169861848
        with self.app.test_client() as c:
            response = c.get(f'/v1/order/{nonexistent_order_id}')
            self.assertEqual(response.status_code, 404)

class Test_Deleting_Order(unittest.TestCase):
    def setUp(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car)
        self.order = Order(
            id=78,
            user_id=789,
            car_id=12,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        c.post('/v1/order', json=self.order)

    def test_deleting_existing_order(self):
        with self.app.test_client() as c:
            # verify that order is in the database
            response = c.get(f'/v1/order')
            self.assertEqual(len(response.json), 1)

            response = c.delete(f'/v1/order/{self.order.id}')
            self.assertEqual(response.status_code, 200)
            response = c.get(f'/v1/order')
            self.assertEqual(response.json, [])

    def test_deleting_nonexistent_order_yields_code_404(self):
        nonexistent_order_id = 651651651
        with self.app.test_client() as c:
            response = c.delete(f'/v1/order/{nonexistent_order_id}')
            self.assertEqual(response.status_code, 404)


class Test_Listing_Updated_Orders_For_Car(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car)
        self.order_1 = Order(
            id=78,
            user_id=789,
            car_id=12,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        self.order_2 = Order(
            id=79,
            user_id=789,
            car_id=12,
            target_stop_id=14,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='4444444444')
        )
        with self.app.test_client() as c:
            c.post('/v1/order', json=self.order_1)
            c.post('/v1/order', json=self.order_2)

    def test_all_orders_not_yet_retrieved_are_listed_as_updated(self):
        with self.app.test_client() as c:
            response = c.get(f'/v1/order/wait/{self.car.id}')
            returned_orders = response.json
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(returned_orders), 2)

    def test_not_updated_orders_cannot_be_listed_repeatedly_without_updating_them(self):
        with self.app.test_client() as c:
            response = c.get(f'/v1/order/wait/{self.car.id}')
            response = c.get(f'/v1/order/wait/{self.car.id}')
            returned_orders = response.json
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(returned_orders), 0)


if __name__ == '__main__':
    unittest.main() # pragma: no coverage