import unittest
import os
import time
from concurrent.futures import ThreadPoolExecutor

import fleet_management_api.database.connection as connection
from fleet_management_api.app import get_app
from fleet_management_api.models import Car, Order, OrderState
import fleet_management_api.database as database


class Test_Waiting_For_Order_States_To_Be_Sent_Do_API(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source("test_db.db")
        self.app = get_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order)

    def test_requesting_order_state_without_wait_mechanism_enabled_immediatelly_returns_empty_list_even_if_no_state_was_sent_yet(self):
        with self.app.test_client() as c:
            response = c.get('/v1/orderstate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

    def test_waiting_for_order_state_when_no_state_was_sent_yet(self):
        order_state = OrderState(id=1, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(c.get, '/v1/orderstate?wait=true')
                time.sleep(0.01)
                executor.submit(c.post, '/v1/orderstate', json=order_state)
                response = future.result()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json), 1)

    def test_all_clients_waiting_get_responses_when_order_state_relevant_for_them_is_sent(self):
        order_state = OrderState(id=1, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_1 = executor.submit(c.get, '/v1/orderstate?wait=true')
                future_2 = executor.submit(c.get, '/v1/orderstate?wait=true')
                future_3 = executor.submit(c.get, '/v1/orderstate?wait=true')
                time.sleep(0.01)
                executor.submit(c.post, '/v1/orderstate', json=order_state)
                for fut in [future_1, future_2, future_3]:
                    response = fut.result()
                    self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Timeouts(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source("test_db.db")
        self.app = get_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order)

    def test_empty_list_is_sent_in_response_to_requests_with_exceeded_timeout(self):
        database.set_content_timeout(100)
        order_state = OrderState(id=1, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_1 = executor.submit(c.get, '/v1/orderstate?wait=true')
                time.sleep(0.05)
                future_2 = executor.submit(c.get, '/v1/orderstate?wait=true')
                time.sleep(0.05)
                executor.submit(c.post, '/v1/orderstate', json=order_state)
                time.sleep(0.05)

                # first request times out and gets empty list
                response = future_1.result()
                self.assertEqual(len(response.json), 0)
                # second request obtains the content before timeout is exceeded
                response = future_2.result()
                self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__=="__main__":
    unittest.main() # pragma: no cover