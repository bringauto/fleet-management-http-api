import unittest
import os
import concurrent.futures as futures
import time

import fleet_management_api.database.connection as _connection
from fleet_management_api.models import Order, Car, MobilePhone, OrderState, OrderStatus
import fleet_management_api.app as _app
from tests._utils.setup_utils import create_platform_hws, create_stops, create_route
from fleet_management_api.api_impl.controllers.order import set_max_n_of_inactive_orders
from fleet_management_api.database.timestamp import timestamp_ms


class Test_Creating_Multiple_Orders_At_Once(unittest.TestCase):

    def setUp(self) -> None:

        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 2)
        create_route(self.app, stop_ids=(1, 2))
        self.car = Car(
            name="test_car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car])

        self.orders = [Order(car_id=1, target_stop_id=1, stop_route_id=1) for _ in range(30)]

    def test_waiting_request_for_new_orders_returns_all_just_created_orders_with_their_default_states(
        self,
    ):
        def get_order_updates():
            with self.app.app.test_client() as c:
                c.get("/v2/management/orderstate?carId=1&wait=true")
                return c.get("/v2/management/order/1")

        with self.app.app.test_client() as c, futures.ThreadPoolExecutor() as executor:
            future = executor.submit(get_order_updates)
            time.sleep(0.15)
            c.post("/v2/management/order", json=self.orders)
            response = future.result()
            orders: list[dict] = response.json
            for order in orders:
                self.assertEqual(order["lastState"]["status"], "to_accept")

    def test_returning_orders_after_some_were_canceled(self):
        set_max_n_of_inactive_orders(5)
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=self.orders)
            for k in range(50):
                state = OrderState(order_id=k + 1, status=OrderStatus.CANCELED)
                c.post("/v2/management/orderstate", json=[state])

            response = c.get("/v2/management/order?carId=1")
            orders = response.json
            self.assertEqual(len(orders), 5)
            for order in orders:
                self.assertEqual(order["lastState"]["status"], "canceled")

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


if __name__ == "__main__":
    unittest.main()  # pragma: no coverage
