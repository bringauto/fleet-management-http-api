import unittest
import os
import sys

sys.path.append(".")

import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import Car, MobilePhone, Order, OrderState, OrderStatus
from tests.utils.setup_utils import create_platform_hws, create_stops, create_route


class Test_Number_Of_Active_Orders(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        _app.clear_n_of_active_orders()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)

    def test_is_increased_whenever_new_order_is_sucessfully_posted(self):
        self.assertEqual(_app.n_of_active_orders(1), 0)
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=order)
            self.assertEqual(_app.n_of_active_orders(1), 1)
            c.post("/v2/management/order", json=order)
            self.assertEqual(_app.n_of_active_orders(1), 2)

    def test_is_decreased_when_order_is_done(self):
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            order_id=c.post("/v2/management/order", json=order).json["id"]
            self.assertEqual(_app.n_of_active_orders(1), 1)

        with self.app.app.test_client() as c:
            done_state = OrderState(status=OrderStatus.DONE, order_id=order_id)
            response = c.post("/v2/management/orderstate", json=done_state)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(_app.n_of_active_orders(1), 0)

    def test_is_decreased_whenever_order_is_canceled(self):
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            order_id=c.post("/v2/management/order", json=order).json["id"]
            self.assertEqual(_app.n_of_active_orders(1), 1)

        with self.app.app.test_client() as c:
            done_state = OrderState(status=OrderStatus.CANCELED, order_id=order_id)
            response = c.post("/v2/management/orderstate", json=done_state)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(_app.n_of_active_orders(1), 0)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Maximum_Number_Of_Active_Orders(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))
        car_1 = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        car_2 = Car(name="car2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="1234567890"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car_1)
            c.post("/v2/management/car", json=car_2)

    def test_max_number_of_orders(self):
        _app.set_max_n_of_active_orders(3)
        order_1 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_2 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_3 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=order_1)
            c.post("/v2/management/order", json=order_2)
            response = c.post("/v2/management/order", json=order_3)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(_app.n_of_active_orders(1), 3)

        order_4 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/order", json=order_4)
            self.assertEqual(response.status_code, 403)

    def test_max_number_of_orders_is_checked_separatly_for_each_car(self):
        _app.set_max_n_of_active_orders(2)
        order_1 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_2 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_3 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_4 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=2)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=order_1)
            c.post("/v2/management/order", json=order_2)
            response = c.post("/v2/management/order", json=order_3)
            self.assertEqual(response.status_code, 403)
            response = c.post("/v2/management/order", json=order_4)
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == '__main__':
    unittest.main()