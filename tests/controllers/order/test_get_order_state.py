import unittest
from unittest.mock import patch, Mock
import os
import time
from concurrent.futures import ThreadPoolExecutor
import sys

sys.path.append(".")

import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import Car, Order, OrderState, MobilePhone
from fleet_management_api.database.db_access import set_content_timeout_ms
from tests.utils.setup_utils import create_platform_hws, create_stops, create_route


class Test_Waiting_For_Order_States_To_Be_Sent_Do_API(unittest.TestCase):
    def setUp(self) -> None:

        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        order = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])

    def test_requesting_order_state_without_wait_mechanism_enabled_immediatelly_returns_empty_list_even_if_no_state_was_sent_yet(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate")
            default_state_timestamp = response.json[0]["timestamp"]
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/orderstate?since={default_state_timestamp+1}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_waiting_for_order_state_when_no_state_was_sent_yet(self):
        order_state = OrderState(order_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(c.get, "/v2/management/orderstate?wait=true&since=0")
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/orderstate", json=[order_state])
                response = future.result()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json), 1)

    def test_all_clients_waiting_get_responses_when_state_relevant_for_them_is_sent(self):
        order_state = OrderState(order_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_1 = executor.submit(c.get, "/v2/management/orderstate?wait=true&since=0")
                future_2 = executor.submit(c.get, "/v2/management/orderstate?wait=true&since=0")
                future_3 = executor.submit(c.get, "/v2/management/orderstate?wait=true&since=0")
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/orderstate", json=[order_state])
                for fut in [future_1, future_2, future_3]:
                    response = fut.result()
                    self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Wait_For_Order_State_For_Given_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        set_content_timeout_ms(1000)
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(
            id=1, name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        order_1 = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        order_2 = Order(
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order_1])
            c.post("/v2/management/order", json=[order_2])

    def test_waiting_for_order_state_for_given_order(self):
        order_state = OrderState(order_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=5) as executor:
                future = executor.submit(c.get, "/v2/management/orderstate?wait=true&since=0")
                future_1 = executor.submit(c.get, "/v2/management/orderstate/1?wait=true&since=0")
                future_2 = executor.submit(c.get, "/v2/management/orderstate/2?wait=true&since=0")
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/orderstate", json=[order_state])

                response = future.result()
                self.assertEqual(len(response.json), 2)
                response = future_1.result()
                self.assertEqual(len(response.json), 1)
                response = future_2.result()
                self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Timeouts(unittest.TestCase):
    def setUp(self) -> None:

        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(
            id=1, name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        order = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])

    def test_empty_list_is_sent_in_response_to_requests_with_exceeded_timeout(self):
        set_content_timeout_ms(150)
        order_state = OrderState(order_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate?&since=0")
            default_state_timestamp = response.json[0]["timestamp"]
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                # this waiting thread exceeds timeout before posting the state
                future_1 = executor.submit(
                    c.get, f"/v2/management/orderstate?wait=true&since={default_state_timestamp+1}"
                )
                # this waiting thread gets the state before timeout is exceeded
                time.sleep(0.1)
                future_2 = executor.submit(
                    c.get, f"/v2/management/orderstate?wait=true&since={default_state_timestamp+1}"
                )
                time.sleep(0.1)
                # this thread posts the state. It is expected that the first waiting thread already exceeded timeout at this point
                # and the second waiting thread gets the state
                executor.submit(c.post, "/v2/management/orderstate", json=[order_state])
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
    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mock_timestamp_ms: Mock) -> None:

        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        order_1 = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        order_2 = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        mock_timestamp_ms.return_value = 0
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order_1])
            c.post("/v2/management/order", json=[order_2])

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_filtering_order_state_by_since_parameter(self, mock_timestamp_ms: Mock):
        order_state_1 = OrderState(order_id=1, status="accepted")
        order_state_2 = OrderState(order_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            mock_timestamp_ms.return_value = 50
            c.post("/v2/management/orderstate", json=[order_state_1])
            mock_timestamp_ms.return_value = 100
            c.post("/v2/management/orderstate", json=[order_state_2])
            response = c.get("/v2/management/orderstate?since=0")
            self.assertEqual(len(response.json), 4)  # type: ignore
            response = c.get("/v2/management/orderstate?since=60")
            self.assertEqual(len(response.json), 1)  # type: ignore
            response = c.get("/v2/management/orderstate?since=100")
            self.assertEqual(len(response.json), 1)  # type: ignore
            response = c.get("/v2/management/orderstate?since=110")
            self.assertEqual(len(response.json), 0)  # type: ignore

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_filtering_order_state_for_specific_order_by_since_parameter(
        self, mock_timestamp_ms: Mock
    ):
        order_state_1 = OrderState(order_id=1, status="accepted")
        order_state_2 = OrderState(order_id=1, status="in_progress")
        order_state_3 = OrderState(order_id=2, status="accepted")
        with self.app.app.test_client() as c:
            mock_timestamp_ms.return_value = 50
            c.post("/v2/management/orderstate", json=[order_state_1])
            mock_timestamp_ms.return_value = 100
            c.post("/v2/management/orderstate", json=[order_state_2])
            mock_timestamp_ms.return_value = 150
            c.post("/v2/management/orderstate", json=[order_state_3])

            response = c.get("/v2/management/orderstate/1?since=110")
            self.assertEqual(len(response.json), 0)  # type: ignore
            response = c.get("/v2/management/orderstate/1?since=60")
            self.assertEqual(len(response.json), 1)  # type: ignore

            response = c.get("/v2/management/orderstate/2?since=110")
            self.assertEqual(len(response.json), 1)  # type: ignore
            response = c.get("/v2/management/orderstate/2?since=160")
            self.assertEqual(len(response.json), 0)  # type: ignore

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_unspecified_since_parameter_yields_the_list_containing_all_the_order_states(
        self, mock_timestamp_ms: Mock
    ):
        order_state_1 = OrderState(order_id=1, status="accepted")
        order_state_2 = OrderState(order_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate/1")

            self.assertEqual(len(response.json), 1)  # type: ignore
            mock_timestamp_ms.return_value = 50
            c.post("/v2/management/orderstate", json=[order_state_1])
            mock_timestamp_ms.return_value = 100
            c.post("/v2/management/orderstate", json=[order_state_2])

            states: list[dict] = c.get("/v2/management/orderstate/1").json  # type: ignore
            self.assertEqual(len(states), 3)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Filtering_Order_States_By_Car_ID(unittest.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mock_timestamp_ms: Mock) -> None:

        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 3)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car_1 = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        car_2 = Car(name="car2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="1234567890"))
        order_1 = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        order_2 = Order(
            priority="high",
            is_visible=True,
            car_id=2,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        mock_timestamp_ms.return_value = 0
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car_1])
            c.post("/v2/management/car", json=[car_2])
            c.post("/v2/management/order", json=[order_1])
            response = c.post("/v2/management/order", json=[order_2])
            assert response.json is not None
            tstamp = response.json[0]["timestamp"]
            assert isinstance(tstamp, int)
            self.since = tstamp + 1

    def test_filtering_existing_order_states_by_car_id(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate?carId=1")
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["orderId"], 1)
            response = c.get("/v2/management/orderstate?carId=2")
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["orderId"], 2)

    def test_getting_order_states_for_nonexistent_car_yields_empty_list(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate?carId=3")
            self.assertEqual(response.json, [])

    def test_waiting_for_order_states_for_given_car(self):
        order_state_1 = OrderState(order_id=1, status="in_progress")
        order_state_2 = OrderState(order_id=2, status="accepted")
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor() as executor:
                future_1 = executor.submit(
                    c.get, f"/v2/management/orderstate?carId=2&wait=true&since={self.since}"
                )
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/orderstate", json=[order_state_1])
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/orderstate", json=[order_state_2])
                response = future_1.result()
                self.assertEqual(len(response.json), 1)
                self.assertEqual(response.json[0]["orderId"], 2)
                self.assertEqual(response.json[0]["status"], "accepted")

    def test_waiting_for_order_states_for_car_created_after_sending_request_for_states(self):
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor() as executor:
                future_1 = executor.submit(
                    c.get, f"/v2/management/orderstate?carId=3&wait=true&since={self.since}"
                )
                time.sleep(0.01)

                car_3 = Car(
                    name="car3", platform_hw_id=3, car_admin_phone=MobilePhone(phone="1234567890")
                )
                order = Order(
                    priority="high",
                    is_visible=True,
                    car_id=3,
                    target_stop_id=1,
                    stop_route_id=1,
                    notification_phone={},
                )
                executor.submit(c.post, "/v2/management/car", json=[car_3])
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/order", json=[order])
                response = future_1.result()
                self.assertEqual(len(response.json), 1)
                self.assertEqual(response.json[0]["orderId"], 3)
                self.assertEqual(response.json[0]["status"], "to_accept")

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == "__main__":
    unittest.main(buffer=True)
