import unittest
from unittest.mock import patch, Mock
import os
import time
from concurrent.futures import ThreadPoolExecutor
import sys

sys.path.append(".")

import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import Car, CarState, MobilePhone
from fleet_management_api.database.db_access import set_content_timeout_ms
from tests.utils.setup_utils import create_platform_hws


class Test_Waiting_For_Car_States_To_Be_Sent_Do_API(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_requesting_car_state_without_wait_mechanism_enabled_immediatelly_returns_empty_list_even_if_no_state_was_sent_yet(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/carstate")
            default_state_timestamp = response.json[0]["timestamp"]
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/carstate?since={default_state_timestamp+1}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_waiting_for_car_state_when_no_state_was_sent_yet(self):
        car_state = CarState(car_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(c.get, "/v2/management/carstate?wait=true&since=0")
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/carstate", json=[car_state])
                response = future.result()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json), 1)

    def test_all_clients_waiting_get_responses_when_state_relevant_for_them_is_sent(self):
        car_state = CarState(car_id=1, status="in_progress")
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_1 = executor.submit(c.get, "/v2/management/carstate?wait=true&since=0")
                future_2 = executor.submit(c.get, "/v2/management/carstate?wait=true&since=0")
                future_3 = executor.submit(c.get, "/v2/management/carstate?wait=true&since=0")
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/carstate", json=[car_state])
                for fut in [future_1, future_2, future_3]:
                    response = fut.result()
                    self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Wait_For_Car_State_For_Given_Car(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        set_content_timeout_ms(1000)
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        car_1 = Car(
            id=1, name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789")
        )
        car_2 = Car(
            id=2, name="car2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="987654321")
        )

        with self.app.app.test_client() as c:
            response = c.post("/v2/management/car", json=[car_1, car_2])
            self.assertEqual(response.status_code, 200)

    def test_waiting_for_car_state_for_given_car(self):
        car_state = CarState(car_id=1, status="idle")
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=5) as executor:
                future = executor.submit(c.get, "/v2/management/carstate?wait=true&since=0")
                future_1 = executor.submit(c.get, "/v2/management/carstate/1?wait=true&since=0")
                future_2 = executor.submit(c.get, "/v2/management/carstate/2?wait=true&since=0")
                time.sleep(0.01)
                executor.submit(c.post, "/v2/management/carstate", json=[car_state])

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
        car = Car(
            id=1, name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_empty_list_is_sent_in_response_to_requests_with_exceeded_timeout(self):
        set_content_timeout_ms(150)
        car_state = CarState(car_id=1, status="charging")
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/carstate?&since=0")
            default_state_timestamp = response.json[0]["timestamp"]
        with self.app.app.test_client() as c:
            with ThreadPoolExecutor(max_workers=2) as executor:
                # this waiting thread exceeds timeout before posting the state
                future_1 = executor.submit(
                    c.get, f"/v2/management/carstate?wait=true&since={default_state_timestamp+1}"
                )
                # this waiting thread gets the state before timeout is exceeded
                time.sleep(0.1)
                future_2 = executor.submit(
                    c.get, f"/v2/management/carstate?wait=true&since={default_state_timestamp+1}"
                )
                time.sleep(0.1)
                # this thread posts the state. It is expected that the first waiting thread already exceeded timeout at this point
                # and the second waiting thread gets the state
                executor.submit(c.post, "/v2/management/carstate", json=[car_state])
                # first request times out and gets empty list
                response = future_1.result()
                self.assertEqual(len(response.json), 0)
                # second request obtains the content before timeout is exceeded
                response = future_2.result()
                self.assertEqual(len(response.json), 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Filtering_Car_States_By_Since_Parameter(unittest.TestCase):
    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mock_timestamp_ms: Mock) -> None:
        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        car_1 = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        car_2 = Car(name="car2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="9876543210"))
        mock_timestamp_ms.return_value = 0
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car_1, car_2])

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_filtering_car_states_by_since_parameter(self, mock_timestamp_ms: Mock):
        car_state_1 = CarState(car_id=1, status="idle")
        car_state_2 = CarState(car_id=1, status="driving")
        with self.app.app.test_client() as c:
            mock_timestamp_ms.return_value = 50
            c.post("/v2/management/carstate", json=[car_state_1])
            mock_timestamp_ms.return_value = 100
            c.post("/v2/management/carstate", json=[car_state_2])
            response = c.get("/v2/management/carstate?since=0")
            self.assertEqual(len(response.json), 4)  # type: ignore
            response = c.get("/v2/management/carstate?since=60")
            self.assertEqual(len(response.json), 1)  # type: ignore
            response = c.get("/v2/management/carstate?since=100")
            self.assertEqual(len(response.json), 1)  # type: ignore
            response = c.get("/v2/management/carstate?since=110")
            self.assertEqual(len(response.json), 0)  # type: ignore

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_filtering_car_states_for_specific_car_by_since_parameter(
        self, mock_timestamp_ms: Mock
    ):
        car_state_1 = CarState(car_id=1, status="idle")
        car_state_2 = CarState(car_id=1, status="driving")
        car_state_3 = CarState(car_id=2, status="out_of_order")
        with self.app.app.test_client() as c:
            mock_timestamp_ms.return_value = 50
            c.post("/v2/management/carstate", json=[car_state_1])
            mock_timestamp_ms.return_value = 100
            c.post("/v2/management/carstate", json=[car_state_2])
            mock_timestamp_ms.return_value = 150
            c.post("/v2/management/carstate", json=[car_state_3])

            response = c.get("/v2/management/carstate/1?since=110")
            self.assertEqual(len(response.json), 0)  # type: ignore
            response = c.get("/v2/management/carstate/1?since=60")
            self.assertEqual(len(response.json), 1)  # type: ignore

            response = c.get("/v2/management/carstate/2?since=110")
            self.assertEqual(len(response.json), 1)  # type: ignore
            response = c.get("/v2/management/carstate/2?since=160")
            self.assertEqual(len(response.json), 0)  # type: ignore

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_unspecified_since_parameter_yields_the_list_containing_all_the_car_states(
        self, mock_timestamp_ms: Mock
    ):
        car_state_1 = CarState(car_id=1, status="idle")
        car_state_2 = CarState(car_id=1, status="idle")
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/carstate/1")

            self.assertEqual(len(response.json), 1)  # type: ignore
            mock_timestamp_ms.return_value = 50
            c.post("/v2/management/carstate", json=[car_state_1])
            mock_timestamp_ms.return_value = 100
            c.post("/v2/management/carstate", json=[car_state_2])

            states: list[dict] = c.get("/v2/management/carstate/1").json  # type: ignore
            self.assertEqual(len(states), 3)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == "__main__":
    unittest.main(buffer=True)
