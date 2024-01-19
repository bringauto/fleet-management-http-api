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


class Test_Deleting_Order(unittest.TestCase):

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
        c.post('/v1/order', json=self.order.to_dict())

    def test_deleting_existing_order(self):
        with self.app.test_client() as c:
            # verify that order is in the database
            response = c.get(f'/v1/order')
            self.assertListEqual(response.json, [self.order.to_dict()])

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
        connection.set_connection_source()
        self.app = get_app().app
        self.car = Car(id=12, name='test_car', platform_id=5)
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car.to_dict())
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
            c.post('/v1/order', json=self.order_1.to_dict())
            c.post('/v1/order', json=self.order_2.to_dict())

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

    def test_order_that_was_updated_before_repeated_request_is_listed_again(self):
        with self.app.test_client() as c:
            response = c.get(f'/v1/order/wait/{self.car.id}')

            # second order is updated
            c.put('/v1/order', json=self.order_2.to_dict())

            # second order is listed again, first one is ignored
            response = c.get(f'/v1/order/wait/{self.car.id}')
            returned_orders = response.json
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(returned_orders), 1)

            # after another request, second order is ignored
            response = c.get(f'/v1/order/wait/{self.car.id}')
            returned_orders = response.json
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(returned_orders), 0)

    def test_listing_updated_orders_for_nonexistent_car_yields_code_404(self):
        nonexistent_car_id = 651651651
        with self.app.test_client() as c:
            response = c.get(f'/v1/order/wait/{nonexistent_car_id}')
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main() # pragma: no coverage