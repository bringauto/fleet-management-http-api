from typing import List, Dict
import unittest
from unittest.mock import patch, Mock
import os
import time
from concurrent.futures import ThreadPoolExecutor

import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import Car, Order, OrderState
import fleet_management_api.database as database


class Test_Waiting_For_Order_States_To_Be_Sent_Do_API(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_test_connection_source("test_db.db")
        self.app = _app.get_test_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order)

    def test_requesting_order_state_without_wait_mechanism_enabled_immediatelly_returns_empty_list_even_if_no_state_was_sent_yet(self):
        with self.app.test_client() as c:
            response = c.get('/v1/orderstate?since=0')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

    def test_waiting_for_order_state_when_no_state_was_sent_yet(self):
        order_state = OrderState(id=1, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(c.get, '/v1/orderstate?wait=true&since=0')
                time.sleep(0.01)
                executor.submit(c.post, '/v1/orderstate', json=order_state)
                response = future.result()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json), 1)

    def test_all_clients_waiting_get_responses_when_order_state_relevant_for_them_is_sent(self):
        order_state = OrderState(id=1, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_1 = executor.submit(c.get, '/v1/orderstate?wait=true&since=0')
                future_2 = executor.submit(c.get, '/v1/orderstate?wait=true&since=0')
                future_3 = executor.submit(c.get, '/v1/orderstate?wait=true&since=0')
                time.sleep(0.01)
                executor.submit(c.post, '/v1/orderstate', json=order_state)
                for fut in [future_1, future_2, future_3]:
                    response = fut.result()
                    self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Wait_For_Order_State_For_Given_Order(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_test_connection_source("test_db.db")
        database.set_content_timeout_ms(1000)
        self.app = _app.get_test_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order_1 = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        order_2 = Order(id=13, user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order_1)
            c.post('/v1/order', json=order_2)

    def test_waiting_for_order_state_for_given_order(self):
        order_state = OrderState(id=1, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=5) as executor:
                future = executor.submit(c.get, '/v1/orderstate?wait=true&since=0')
                future_1 = executor.submit(c.get, '/v1/orderstate/12?wait=true&since=0')
                future_2 = executor.submit(c.get, '/v1/orderstate/13?wait=true&since=0')
                time.sleep(0.01)
                executor.submit(c.post, '/v1/orderstate', json=order_state)

                response = future.result()
                self.assertEqual(len(response.json), 1)
                response = future_1.result()
                self.assertEqual(len(response.json), 1)
                response = future_2.result()
                self.assertEqual(len(response.json), 0)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Timeouts(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_test_connection_source("test_db.db")
        self.app = _app.get_test_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order)

    def test_empty_list_is_sent_in_response_to_requests_with_exceeded_timeout(self):
        database.set_content_timeout_ms(100)
        order_state = OrderState(id=1, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_1 = executor.submit(c.get, '/v1/orderstate?wait=true&since=0')
                time.sleep(0.05)
                future_2 = executor.submit(c.get, '/v1/orderstate?wait=true&since=0')
                time.sleep(0.05)
                executor.submit(c.post, '/v1/orderstate', json=order_state)
                time.sleep(0.05)
                # first request times out and gets empty list
                response = future_1.result()
                self.assertEqual(len(response.json), 0)
                # second request obtains the content before timeout is exceeded
                response = future_2.result()
                self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Filtering_Order_State_By_Since_Parameter(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_test_connection_source("test_db.db")
        self.app = _app.get_test_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order_1 = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        order_2 = Order(id=13, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order_1)
            c.post('/v1/order', json=order_2)

    @patch('fleet_management_api.database.timestamp.timestamp_ms')
    def test_filtering_order_state_by_since_parameter(self, mock_timestamp_ms: Mock):
        order_state_1 = OrderState(id=1, order_id=12, status="accepted")
        order_state_2 = OrderState(id=2, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            mock_timestamp_ms.return_value = 50
            c.post('/v1/orderstate', json=order_state_1)
            mock_timestamp_ms.return_value = 100
            c.post('/v1/orderstate', json=order_state_2)
            response = c.get('/v1/orderstate?since=0')
            self.assertEqual(len(response.json), 2)
            response = c.get('/v1/orderstate?since=60')
            self.assertEqual(len(response.json), 1)
            response = c.get('/v1/orderstate?since=100')
            self.assertEqual(len(response.json), 1)
            response = c.get('/v1/orderstate?since=110')
            self.assertEqual(len(response.json), 0)


    @patch('fleet_management_api.database.timestamp.timestamp_ms')
    def test_filtering_order_state_for_specific_order_by_since_parameter(self, mock_timestamp_ms: Mock):
        order_state_1 = OrderState(id=1, order_id=12, status="accepted")
        order_state_2 = OrderState(id=2, order_id=12, status="in_progress")
        order_state_3 = OrderState(id=3, order_id=13, status="accepted")
        with self.app.test_client() as c:
            mock_timestamp_ms.return_value = 50
            c.post('/v1/orderstate', json=order_state_1)
            mock_timestamp_ms.return_value = 100
            c.post('/v1/orderstate', json=order_state_2)
            mock_timestamp_ms.return_value = 150
            c.post('/v1/orderstate', json=order_state_3)

            response = c.get('/v1/orderstate/12?since=110')
            self.assertEqual(len(response.json), 0)
            response = c.get('/v1/orderstate/12?since=60')
            self.assertEqual(len(response.json), 1)

            response = c.get('/v1/orderstate/13?since=110')
            self.assertEqual(len(response.json), 1)
            response = c.get('/v1/orderstate/13?since=160')
            self.assertEqual(len(response.json), 0)

    @patch('fleet_management_api.database.timestamp.timestamp_ms')
    def test_unspecified_since_parameter_yields_the_list_containing_the_newest_order_state_or_empty_list(self, mock_timestamp_ms: Mock):
        order_state_1 = OrderState(id=1, order_id=12, status="accepted")
        order_state_2 = OrderState(id=2, order_id=12, status="in_progress")
        with self.app.test_client() as c:
            response = c.get('/v1/orderstate/12')

            self.assertEqual(len(response.json), 0)
            mock_timestamp_ms.return_value = 50
            c.post('/v1/orderstate', json=order_state_1)
            mock_timestamp_ms.return_value = 100
            c.post('/v1/orderstate', json=order_state_2)

            states: List[Dict] = c.get('/v1/orderstate/12').json
            self.assertEqual(len(states), 1)
            self.assertEqual(states[0]["id"], 2)

    def test_waiting_with_since_parameter_unspecified_makes_the_api_wait_for_some_new_state_to_come(self):
        old_state = OrderState(id=123, order_id=12, status="accepted")
        new_state = OrderState(id=456, order_id=12, status="accepted")
        with self.app.test_client() as c:
            c.post('/v1/orderstate', json=old_state)
            with ThreadPoolExecutor(max_workers=5) as executor:
                future = executor.submit(c.get, '/v1/orderstate/12?wait=true')
                time.sleep(0.01)
                executor.submit(c.post, '/v1/orderstate', json=new_state)
                response = future.result()
                states = response.json
                self.assertEqual(len(states), 1)
                self.assertEqual(states[0]["id"], 456)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")



if __name__=="__main__":
    unittest.main() # pragma: no cover