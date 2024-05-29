import unittest
import os
import sys

sys.path.append(".")

import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
import fleet_management_api.api_impl.controllers.order as _order
from fleet_management_api.api_impl.controllers.order import (
    clear_active_orders,
    clear_inactive_orders,
)
from fleet_management_api.models import Car, MobilePhone, Order, OrderState, OrderStatus
from tests.utils.setup_utils import create_platform_hws, create_stops, create_route
from fleet_management_api.api_impl.controllers.order import (
    n_of_active_orders,
    n_of_inactive_orders,
    set_max_n_of_active_orders,
    set_max_n_of_inactive_orders,
)


class Test_Number_Of_Active_Orders(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        clear_active_orders()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_is_increased_whenever_new_order_is_sucessfully_posted(self):
        self.assertEqual(n_of_active_orders(1), 0)
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            self.assertEqual(n_of_active_orders(1), 1)
            c.post("/v2/management/order", json=[order])
            self.assertEqual(n_of_active_orders(1), 2)

    def test_is_decreased_when_order_is_done(self):
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            order_id = c.post("/v2/management/order", json=[order]).json[0]["id"]
            self.assertEqual(n_of_active_orders(1), 1)

        with self.app.app.test_client() as c:
            done_state = OrderState(status=OrderStatus.DONE, order_id=order_id)
            response = c.post("/v2/management/orderstate", json=[done_state])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(n_of_active_orders(1), 0)

    def test_is_decreased_whenever_order_is_canceled(self):
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            order_id = c.post("/v2/management/order", json=[order]).json[0]["id"]
            self.assertEqual(n_of_active_orders(1), 1)

        with self.app.app.test_client() as c:
            done_state = OrderState(status=OrderStatus.CANCELED, order_id=order_id)
            response = c.post("/v2/management/orderstate", json=[done_state])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(n_of_active_orders(1), 0)

    def test_is_decreased_when_order_is_deleted(self):
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            self.assertEqual(n_of_active_orders(1), 1)
            c.delete("/v2/management/order/1/1")
            self.assertEqual(n_of_active_orders(1), 0)

    def test_the_number_is_unchanged_when_restarting_the_application(self):
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order, order])
            self.assertEqual(n_of_active_orders(car_id=1), 2)
        self.app = _app.get_test_app()
        clear_active_orders()
        with self.app.app.test_client() as c:
            self.assertEqual(n_of_active_orders(car_id=1), 2)

    def tearDown(self) -> None:  # pragma: no cover
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
            c.post("/v2/management/car", json=[car_1, car_2])

    def test_max_number_of_orders(self):
        set_max_n_of_active_orders(3)
        order_1 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_2 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_3 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order_1])
            c.post("/v2/management/order", json=[order_2])
            response = c.post("/v2/management/order", json=[order_3])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(n_of_active_orders(1), 3)

        order_4 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/order", json=[order_4])
            self.assertEqual(response.status_code, 403)

    def test_max_number_of_orders_is_checked_separately_for_each_car(self):
        set_max_n_of_active_orders(2)
        order_1 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_2 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_3 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_4 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=2)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order_1, order_2])
            response = c.post("/v2/management/order", json=[order_3])
            self.assertEqual(response.status_code, 403)
            response = c.post("/v2/management/order", json=[order_4])
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Number_Of_Inactive_Orders_Lower_Than_Maximum(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        clear_active_orders()
        clear_inactive_orders()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_is_increased_or_when_order_receives_done_status(self):
        self.assertEqual(n_of_active_orders(1), 0)
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            self.assertEqual(n_of_active_orders(1), 1)
            self.assertEqual(n_of_inactive_orders(1), 0)
            c.post("/v2/management/orderstate", json=[done_state])
            self.assertEqual(n_of_inactive_orders(1), 1)

    def test_is_decreased_when_done_order_is_deleted(self):
        self.assertEqual(n_of_active_orders(1), 0)
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            c.post("/v2/management/orderstate", json=[done_state])
            self.assertEqual(n_of_inactive_orders(1), 1)
            c.delete("/v2/management/order/1/1")
            self.assertEqual(n_of_inactive_orders(1), 0)

    def test_is_increased_or_when_order_receives_canceled_status(self):
        self.assertEqual(n_of_active_orders(1), 0)
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        canceled_state = OrderState(status=OrderStatus.CANCELED, order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            self.assertEqual(n_of_inactive_orders(1), 0)
            c.post("/v2/management/orderstate", json=[canceled_state])
            self.assertEqual(n_of_inactive_orders(1), 1)

    def test_is_decreased_when_canceled_order_is_deleted(self):
        self.assertEqual(n_of_active_orders(1), 0)
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        canceled_state = OrderState(status=OrderStatus.CANCELED, order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            c.post("/v2/management/orderstate", json=[canceled_state])
            self.assertEqual(n_of_inactive_orders(1), 1)
            c.delete("/v2/management/order/1/1")
            self.assertEqual(n_of_inactive_orders(1), 0)

    def test_the_number_is_unchanged_when_restarting_the_application(self):
        order = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order, order])
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=1)]
            )
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=2)]
            )
            self.assertEqual(n_of_inactive_orders(car_id=1), 2)
        self.app = _app.get_test_app()
        clear_active_orders()
        with self.app.app.test_client() as c:
            self.assertEqual(n_of_inactive_orders(car_id=1), 2)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Automatic_Removal_Of_Inactive_Orders(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        clear_active_orders()
        clear_inactive_orders()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_when_new_order_is_marked_as_done_and_maximum_number_of_inactive_orders_is_already_reached(
        self,
    ):
        set_max_n_of_active_orders(None)
        set_max_n_of_inactive_orders(2)
        order_1 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_2 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_3 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order_1, order_2])
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=1)]
            )
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=2)]
            )
            self.assertEqual(n_of_inactive_orders(1), 2)
            c.post("/v2/management/order", json=[order_3])
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=3)]
            )
            self.assertEqual(n_of_inactive_orders(1), 2)
            self.assertNotIn(1, _order._inactive_orders[1])
            self.assertIn(3, _order._inactive_orders[1])

    def test_starts_from_order_that_was_completed_first(self):
        set_max_n_of_active_orders(None)
        set_max_n_of_inactive_orders(2)
        order_1 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_2 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        order_3 = Order(user_id=1, target_stop_id=1, stop_route_id=1, car_id=1)
        car_id = 1
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order_1, order_2])
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=2)]
            )
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=1)]
            )
            self.assertEqual(n_of_inactive_orders(car_id), 2)
            c.post("/v2/management/order", json=[order_3])
            c.post(
                "/v2/management/orderstate", json=[OrderState(status=OrderStatus.DONE, order_id=3)]
            )
            self.assertEqual(n_of_inactive_orders(car_id), 2)
            # order 2 is removed as it was COMPLETED first, regardless of being CREATED after order 1
            self.assertListEqual(_order._inactive_orders[car_id], [1, 3])

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == "__main__":
    unittest.main(buffer=True)
