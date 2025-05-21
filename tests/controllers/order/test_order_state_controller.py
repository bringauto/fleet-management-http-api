import unittest
from unittest.mock import patch, Mock
import os

import fleet_management_api.app as _app
from fleet_management_api.models import (
    OrderState,
    Order,
    Car,
    OrderStatus,
    GNSSPosition,
    MobilePhone,
    Tenant,
)
import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.api_impl.auth_controller import (
    get_test_public_key,
    set_auth_params,
    generate_test_keys,
)

from tests._utils.setup_utils import create_platform_hws, create_stops, create_route
from tests._utils.constants import TEST_TENANT_NAME


MAX_STORED_STATES = 50


class Test_Adding_State_Of_Existing_Order(unittest.TestCase):
    def setUp(self) -> None:

        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2, 3))
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            id=12,
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])

    def test_adding_state_to_existing_order(self):
        order_state = OrderState(id=1, status="to_accept", order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[order_state])
            self.assertEqual(response.status_code, 200)

    def test_adding_state_to_none_existing_order_returns_code_404(self):
        order_state = OrderState(id=1, status="to_accept", order_id=4651684651)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[order_state])
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_state_returns_code_400(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[{}])
            self.assertEqual(response.status_code, 400)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Adding_State_Using_Example_From_Spec(unittest.TestCase):
    def test_adding_state_using_example_from_spec(self):
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            spec = c.get("/v2/management/openapi.json").json
            example = spec["components"]["schemas"]["OrderState"]["example"]
            order = Order(
                priority="high",
                is_visible=True,
                car_id=1,
                target_stop_id=1,
                stop_route_id=1,
                notification_phone={},
            )
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])

            response = c.post("/v2/management/orderstate", json=[example])
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Getting_All_Order_States_For_Given_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])

    def test_a_single_order_state_is_automatically_created_when_order_is_created_with_to_accept_status(
        self,
    ):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_getting_all_existing_states_for_given_order_by_specifying_since_as_zero(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/orderstate", json=[order_state_1])
            c.post("/v2/management/orderstate", json=[order_state_2])
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)

    def test_getting_all_existing_states_for_given_order_without_specifying_since(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/orderstate", json=[order_state_1])
            c.post("/v2/management/orderstate", json=[order_state_2])
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Getting_Order_State_For_Given_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
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
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order_1])
            c.post("/v2/management/order", json=[order_2])

    def test_getting_order_state_for_nonexisting_order_returns_code_404(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/4651684651")
            self.assertEqual(response.status_code, 404)

    def test_getting_all_order_states(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/orderstate", json=[order_state_1])
            c.post("/v2/management/orderstate", json=[order_state_2])
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertListEqual(
                [state["status"] for state in response.json], ["to_accept", "to_accept", "canceled"]
            )

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Maximum_Number_Of_States_Stored(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
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
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order_1])
            c.post("/v2/management/order", json=[order_2])
        self.max_n = _db_models.OrderStateDB.max_n_of_stored_states()

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(
        self,
    ):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            oldest_state = OrderState(status="to_accept", order_id=1)
            c.post("/v2/management/orderstate", json=[oldest_state])
            for i in range(1, self.max_n - 2):
                order_state = OrderState(status="to_accept", order_id=1)
                c.post("/v2/management/orderstate", json=[order_state])
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), self.max_n - 1)

            order_state = OrderState(status="to_accept", order_id=1)
            c.post("/v2/management/orderstate", json=[order_state])
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), self.max_n)

            newest_state = OrderState(id=self.max_n + 1, status="to_accept", order_id=1)
            c.post("/v2/management/orderstate", json=[newest_state])
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), self.max_n)
            self.assertTrue(isinstance(response.json, list))

            ids = [state["id"] for state in response.json]
            self.assertFalse(oldest_state.id in ids)
            self.assertTrue(newest_state.id in ids)

    def test_total_number_of_order_states_does_not_exceed_number_of_orders_times_the_maximum_number_of_states_for_single_order(
        self,
    ):
        _db_models.OrderStateDB.set_max_n_of_stored_states(50)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            order_state_1 = OrderState(status="to_accept", order_id=1)
            for _ in range(100):
                c.post("/v2/management/orderstate", json=[order_state_1])
            order_state_2 = OrderState(status="to_accept", order_id=2)
            for _ in range(100):
                c.post("/v2/management/orderstate", json=[order_state_2])

            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 50)

            response = c.get("/v2/management/orderstate/2?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 50)

            response = c.get("/v2/management/orderstate?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 100)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Deleting_Order_States_When_Deleting_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        other_order = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])
            c.post("/v2/management/order", json=[other_order])

    def test_deleting_order_deletes_all_its_states(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        other_order_state = OrderState(status="canceled", order_id=2)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/orderstate", json=[order_state_1])
            c.post("/v2/management/orderstate", json=[order_state_2])
            c.post("/v2/management/orderstate", json=[other_order_state])
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(len(response.json), 3)

            c.delete("/v2/management/order/1/1")
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 404)

            response = c.get("/v2/management/orderstate?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Accepting_Order_States_After_Receiving_State_With_Final_Status(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            priority="high",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])

    def test_sending_single_order_state_after_DONE_status_has_been_received_yield_403_code(self):
        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        next_state_1 = OrderState(status=OrderStatus.TO_ACCEPT, order_id=1)
        next_state_2 = OrderState(status=OrderStatus.ACCEPTED, order_id=1)
        next_state_3 = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        next_state_4 = OrderState(status=OrderStatus.CANCELED, order_id=1)
        next_state_5 = OrderState(status=OrderStatus.DONE, order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[done_state])
            self.assertEqual(response.status_code, 200)

            for next_state in [
                next_state_1,
                next_state_2,
                next_state_3,
                next_state_4,
                next_state_5,
            ]:
                response = c.post("/v2/management/orderstate", json=[next_state])
                self.assertEqual(response.status_code, 403)

            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.DONE)

    def test_sending_single_order_state_after_CANCELED_status_has_been_received_yields_403_code(
        self,
    ):
        canceled_state = OrderState(status=OrderStatus.CANCELED, order_id=1)
        next_state_1 = OrderState(status=OrderStatus.TO_ACCEPT, order_id=1)
        next_state_2 = OrderState(status=OrderStatus.ACCEPTED, order_id=1)
        next_state_3 = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        next_state_4 = OrderState(status=OrderStatus.DONE, order_id=1)
        next_state_5 = OrderState(status=OrderStatus.CANCELED, order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[canceled_state])
            self.assertEqual(response.status_code, 200)

            for next_state in [
                next_state_1,
                next_state_2,
                next_state_3,
                next_state_4,
                next_state_5,
            ]:
                response = c.post("/v2/management/orderstate", json=[next_state])
                self.assertEqual(response.status_code, 403)

            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.CANCELED)

    def test_sending_large_number_of_order_states_before_done_state(self):
        some_state = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        _db_models.OrderStateDB.set_max_n_of_stored_states(MAX_STORED_STATES)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            for _ in range(60):
                response = c.post("/v2/management/orderstate", json=[some_state])
                self.assertEqual(response.status_code, 200)

        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[done_state])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.DONE)
            response = c.post("/v2/management/orderstate", json=[some_state])
            self.assertEqual(response.status_code, 403)

    def test_receiving_states_after_final_state_does_not_trigger_autodeletion_of_oldest_states(
        self,
    ):
        # set up the database
        max_n = 3
        _db_models.OrderStateDB.set_max_n_of_stored_states(max_n)

        # push the done state, check there is the default and final state only
        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[done_state])
            self.assertEqual(response.status_code, 200)

            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(
                [state["status"] for state in response.json],
                [OrderStatus.TO_ACCEPT, OrderStatus.DONE],
            )

        # push more states
        some_state = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            for _ in range(max_n):
                response = c.post("/v2/management/orderstate", json=[some_state])
                self.assertEqual(response.status_code, 403)  # should be rejected

        # check the states did not change
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(
                [state["status"] for state in response.json],
                [OrderStatus.TO_ACCEPT, OrderStatus.DONE],
            )

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Recongnizing_Done_And_Canceled_Orders_After_Restarting_Application(unittest.TestCase):

    def test_done_state(self):
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            is_visible=True, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={}
        )
        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        next_state = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])
            c.post("/v2/management/orderstate", json=[done_state])

        self.app = _app.get_test_app(use_previous=True)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.DONE)
            response = c.post("/v2/management/orderstate", json=[next_state])
            self.assertEqual(response.status_code, 403)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.DONE)

    def test_canceled_state(self):
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            is_visible=True, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={}
        )
        canceled_state = OrderState(status=OrderStatus.CANCELED, order_id=1)
        next_state = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])
            c.post("/v2/management/orderstate", json=[canceled_state])

        self.app = _app.get_test_app(use_previous=True)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.CANCELED)
            response = c.post("/v2/management/orderstate", json=[next_state])
            self.assertEqual(response.status_code, 403)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.CANCELED)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


POSITION = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
PHONE = MobilePhone(phone="123456789")


class Test_Returning_Last_N_Order_States(unittest.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mocked_timestamp: Mock) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 1)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        order = Order(
            is_visible=True, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone=PHONE
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 0
            response = c.post("/v2/management/car", json=[car])
            assert response.json is not None
            car_id = response.json[0]["id"]
            order.car_id = car_id
            response = c.post("/v2/management/order", json=[order])
            assert response.json is not None
            order_id = response.json[0]["id"]

        state_1 = OrderState(status="accepted", order_id=order_id)
        state_2 = OrderState(status="in_progress", order_id=order_id)

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 1000
            c.post("/v2/management/orderstate", json=[state_1])
            mocked_timestamp.return_value = 2000
            c.post("/v2/management/orderstate", json=[state_2])

    def test_returning_last_1_state(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "in_progress")

    def test_returning_last_2_states(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate?lastN=2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["status"], "accepted")
            self.assertEqual(response.json[1]["status"], "in_progress")

    def test_setting_last_n_to_higher_value_than_number_of_existing_states_yields_all_existing_states(
        self,
    ):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate?lastN=100000")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["status"], "to_accept")
            self.assertEqual(response.json[1]["status"], "accepted")
            self.assertEqual(response.json[2]["status"], "in_progress")

    def test_returning_last_two_states_newer_than_given_timestamp(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate?lastN=2&since=1500")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "in_progress")

    def test_returning_last_timestamp_with_identical_timestamps_returns_the_one_with_higher_id(
        self,
    ):
        state_3 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/orderstate", json=[state_3])
            response = c.get("/v2/management/orderstate?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "canceled")

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Returning_Last_N_Car_States_For_Given_Car(unittest.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mocked_timestamp: Mock) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        create_stops(self.app, 2)
        create_route(self.app, stop_ids=(1, 2))
        car_1 = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        self.order_1 = Order(
            is_visible=True, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone=PHONE
        )
        self.order_2 = Order(
            is_visible=True, car_id=1, target_stop_id=2, stop_route_id=1, notification_phone=PHONE
        )

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 0
            c.post("/v2/management/car", json=[car_1])
            c.post("/v2/management/order", json=[self.order_1, self.order_2])

        state_1 = OrderState(status="accepted", order_id=1)
        state_2 = OrderState(status="in_progress", order_id=1)
        state_3 = OrderState(status="accepted", order_id=2)
        state_4 = OrderState(status="done", order_id=2)

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 1000
            c.post("/v2/management/orderstate", json=[state_1, state_3])
            mocked_timestamp.return_value = 2000
            c.post("/v2/management/orderstate", json=[state_2, state_4])

    def test_returning_last_1_state_for_given_car(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/1?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "in_progress")

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/2?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "done")

    def test_returning_last_2_states_for_given_car(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/orderstate/1?lastN=2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["status"], "accepted")
            self.assertEqual(response.json[1]["status"], "in_progress")

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Car_States_Without_Tenant_In_Cookies(unittest.TestCase):

    def setUp(self, *args) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True, predef_api_key="test_key")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post(
                "/v2/management/tenant?api_key=test_key",
                json=[Tenant(name="tenant_A"), Tenant(name="tenant_B"), Tenant(name="tenant_C")],
            )

        create_platform_hws(self.app, 1, tenant="tenant_A", api_key="test_key")
        create_platform_hws(self.app, 2, tenant="tenant_B", api_key="test_key")
        create_platform_hws(self.app, 3, tenant="tenant_C", api_key="test_key")

        create_stops(self.app, 1, tenant="tenant_A", api_key="test_key")
        create_stops(self.app, 1, tenant="tenant_B", api_key="test_key")
        create_stops(self.app, 1, tenant="tenant_C", api_key="test_key")

        create_route(self.app, stop_ids=(1,), tenant="tenant_A", api_key="test_key")
        create_route(self.app, stop_ids=(2,), tenant="tenant_B", api_key="test_key")
        create_route(self.app, stop_ids=(3,), tenant="tenant_C", api_key="test_key")

        car_1 = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        car_2 = Car(platform_hw_id=2, name="car3", car_admin_phone=PHONE)
        car_3 = Car(platform_hw_id=3, name="car6", car_admin_phone=PHONE)

        order_1 = Order(car_id=1, target_stop_id=1, stop_route_id=1, notification_phone=PHONE)
        order_2 = Order(car_id=2, target_stop_id=2, stop_route_id=2, notification_phone=PHONE)
        order_3 = Order(car_id=3, target_stop_id=3, stop_route_id=3, notification_phone=PHONE)

        with self.app.app.test_client("tenant_A") as c:
            c.set_cookie("", "tenant", "tenant_A")
            response = c.post("/v2/management/car?api_key=test_key", json=[car_1])
            assert response.status_code == 200, response.json
            response = c.post("/v2/management/order?api_key=test_key", json=[order_1])
            assert response.status_code == 200, response.json
        with self.app.app.test_client("tenant_B") as c:
            c.set_cookie("", "tenant", "tenant_B")
            response = c.post("/v2/management/car?api_key=test_key", json=[car_2])
            assert response.status_code == 200, response.json
            response = c.post("/v2/management/order?api_key=test_key", json=[order_2])
            assert response.status_code == 200, response.json
        with self.app.app.test_client("tenant_C") as c:
            c.set_cookie("", "tenant", "tenant_C")
            response = c.post("/v2/management/car?api_key=test_key", json=[car_3])
            assert response.status_code == 200, response.json
            response = c.post("/v2/management/order?api_key=test_key", json=[order_3])
            assert response.status_code == 200, response.json

        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")

    def test_accessing_order_states_without_specifying_tenant_yields_states_of_orders_owned_by_accessible_tenants(
        self,
    ) -> None:
        with self.app.app.test_client() as c:
            response = c.get(
                "/v2/management/orderstate",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
            )
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 2)
            for state in response.json:
                self.assertEqual(state["status"], "to_accept")

    def test_posting_order_state_is_allowed_without_cookie_set_if_order_is_owned_by_accessible_tenant(
        self,
    ):

        # order with id 1 is owned by tenant_A
        state = OrderState(status="accepted", order_id=1)
        with self.app.app.test_client() as c:
            c.set_cookie("", "tenant", "")
            # post to car owned by tenant_A, that is accessible (present in the token)
            response = c.post(
                "/v2/management/orderstate",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
                json=[state],
            )
            self.assertEqual(response.status_code, 200)
            assert response.json is not None, response.json
            self.assertEqual(response.json[0]["status"], "accepted")
            self.assertEqual(response.json[0]["orderId"], 1)

    def test_posting_order_state_is_not_allowed_if_order_owned_by_inaccessible_tenant(self):
        # order with id 3 is owned by tenant_C
        state = OrderState(status="accepted", order_id=3)
        with self.app.app.test_client() as c:
            print(c.get("/v2/management/order?test_").json)
            c.set_cookie("", "tenant", "")
            # post to order owned by tenant_C, that is inaccessible (missing from the token)
            response = c.post(
                "/v2/management/orderstate",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
                json=[state],
            )
            self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no coverage
