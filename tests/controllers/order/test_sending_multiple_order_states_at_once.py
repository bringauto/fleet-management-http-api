import unittest

import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import Car, Order, OrderState, MobilePhone
from tests._utils.setup_utils import create_platform_hws, create_stops, create_route
from fleet_management_api.api_impl.controllers.order_state import (
    _trim_states_after_done_or_canceled,
)
from fleet_management_api.api_impl.controllers.order import (
    set_max_n_of_active_orders,
    set_max_n_of_inactive_orders,
)
from tests._utils.constants import TEST_TENANT_NAME


class Test_Sending_Done_And_Other_Order_States_In_Single_Request(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app(use_previous=True)
        set_max_n_of_active_orders(5)
        set_max_n_of_inactive_orders(5)
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890"))
        order_1 = Order(car_id=1, target_stop_id=1, stop_route_id=1)
        order_2 = Order(car_id=1, target_stop_id=1, stop_route_id=1)
        order_3 = Order(car_id=1, target_stop_id=1, stop_route_id=1)

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order_1, order_2, order_3])

    def test_sending_in_progress_first_and_done_second_states_in_single_request_is_allowed(self):
        in_progress = OrderState(order_id=1, status="in_progress")
        done = OrderState(order_id=1, status="done")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[in_progress, done])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(len(response.json), 3)
            statuses = [state["status"] for state in sorted(response.json, key=lambda x: x["id"])]
            self.assertEqual(statuses[-2], "in_progress")
            self.assertEqual(statuses[-1], "done")

    def test_sending_done_first_and_in_progress_second_states_in_single_request_adds_only_done_state(
        self,
    ):
        in_progress = OrderState(order_id=1, status="in_progress")
        done = OrderState(order_id=1, status="done")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/orderstate", json=[done, in_progress])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(len(response.json), 2)
            statuses = [state["status"] for state in sorted(response.json, key=lambda x: x["id"])]
            self.assertEqual(statuses[-2], "to_accept")  # default state
            self.assertEqual(statuses[-1], "done")

    def test_check_is_done_for_each_order_individually(self):
        in_progress_1 = OrderState(order_id=1, status="in_progress")
        done_1 = OrderState(order_id=1, status="done")

        done_2 = OrderState(order_id=2, status="done")
        in_progress_2 = OrderState(order_id=2, status="in_progress")  # will not be posted

        accepted_3 = OrderState(order_id=3, status="accepted")
        canceled_3 = OrderState(order_id=3, status="canceled")
        accepted_3a = OrderState(order_id=3, status="accepted")  # will not be posted

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post(
                "/v2/management/orderstate",
                json=[
                    in_progress_1,
                    done_1,
                    done_2,
                    in_progress_2,
                    accepted_3,
                    canceled_3,
                    accepted_3a,
                ],
            )
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(len(response.json), 3)
            response = c.get("/v2/management/orderstate/2")
            self.assertEqual(len(response.json), 2)
            response = c.get("/v2/management/orderstate/3")
            self.assertEqual(len(response.json), 3)


class Test_Removing_States_From_Posted_List_Of_States_When_Final_State_Is_Also_Being_Posted(
    unittest.TestCase
):

    def test_all_states_of_the_same_order_are_kept_if_final_state_is_the_last_one(self):
        states = [
            OrderState(order_id=1, status="in_progress"),
            OrderState(order_id=1, status="done"),
        ]
        states = _trim_states_after_done_or_canceled(states)
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].status, "in_progress")
        self.assertEqual(states[1].status, "done")

    def test_removing_states_coming_after_final_states(self):
        states = [
            OrderState(order_id=1, status="done"),
            OrderState(order_id=1, status="in_progress"),
        ]
        states = _trim_states_after_done_or_canceled(states)
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].status, "done")

    def test_states_of_different_orders_are_handled_separately(self):
        states = [
            OrderState(order_id=1, status="done"),
            OrderState(order_id=1, status="in_progress"),
            OrderState(order_id=2, status="in_progress"),
        ]
        states = _trim_states_after_done_or_canceled(states)
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].status, "done")
        self.assertEqual(states[1].status, "in_progress")


if __name__ == "__main__":
    unittest.main()
