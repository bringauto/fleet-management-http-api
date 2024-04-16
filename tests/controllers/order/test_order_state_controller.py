import unittest
import sys

sys.path.append(".")

import fleet_management_api.app as _app
from fleet_management_api.models import OrderState, Order, Car, OrderStatus
import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_models as _db_models
from tests.utils.setup_utils import create_platform_hws, create_stops, create_route


class Test_Adding_State_Of_Existing_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2, 3))
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            id=12,
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order)

    def test_adding_state_to_existing_order(self):
        order_state = OrderState(id=1, status="to_accept", order_id=1)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/orderstate", json=order_state)
            self.assertEqual(response.status_code, 200)

    def test_adding_state_to_none_existing_order_returns_code_404(self):
        order_state = OrderState(id=1, status="to_accept", order_id=4651684651)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/orderstate", json=order_state)
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_state_returns_code_400(self):
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/orderstate", json={})
            self.assertEqual(response.status_code, 400)


class Test_Adding_State_Using_Example_From_Spec(unittest.TestCase):
    def test_adding_state_using_example_from_spec(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
        with self.app.app.test_client() as c:
            spec = c.get("/v2/management/openapi.json").json
            example = spec["components"]["schemas"]["OrderState"]["example"]
            order = Order(
                priority="high",
                user_id=1,
                car_id=1,
                target_stop_id=1,
                stop_route_id=1,
                notification_phone={},
            )
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order)

            response = c.post("/v2/management/orderstate", json=example)
            self.assertEqual(response.status_code, 200)


class Test_Getting_All_Order_States_For_Given_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order)

    def test_a_single_order_state_is_automatically_created_when_order_is_created_with_to_accept_status(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_getting_all_existing_states_for_given_order_by_specifying_since_as_zero(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=order_state_1)
            c.post("/v2/management/orderstate", json=order_state_2)
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)

    def test_getting_all_existing_states_for_given_order_without_specifying_since(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=order_state_1)
            c.post("/v2/management/orderstate", json=order_state_2)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)


class Test_Getting_Order_State_For_Given_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order_1 = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        order_2 = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order_1)
            c.post("/v2/management/order", json=order_2)

    def test_getting_order_state_for_nonexisting_order_returns_code_404(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate/4651684651")
            self.assertEqual(response.status_code, 404)

    def test_getting_all_order_states(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=order_state_1)
            c.post("/v2/management/orderstate", json=order_state_2)
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertListEqual(
                [state["status"] for state in response.json], ["to_accept", "to_accept", "canceled"]
            )


class Test_Maximum_Number_Of_States_Stored(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order_1 = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        order_2 = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order_1)
            c.post("/v2/management/order", json=order_2)
        self.max_n = _db_models.OrderStateDBModel.max_n_of_stored_states()

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(
        self,
    ):
        with self.app.app.test_client() as c:
            oldest_state = OrderState(status="to_accept", order_id=1)
            c.post("/v2/management/orderstate", json=oldest_state)
            for i in range(1, self.max_n - 2):
                order_state = OrderState(status="to_accept", order_id=1)
                c.post("/v2/management/orderstate", json=order_state)
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), self.max_n - 1)

            order_state = OrderState(status="to_accept", order_id=1)
            c.post("/v2/management/orderstate", json=order_state)
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), self.max_n)

            newest_state = OrderState(id=self.max_n + 1, status="to_accept", order_id=1)
            c.post("/v2/management/orderstate", json=newest_state)
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
        _db_models.OrderStateDBModel.set_max_n_of_stored_states(50)
        with self.app.app.test_client() as c:
            order_state_1 = OrderState(status="to_accept", order_id=1)
            for _ in range(200):
                c.post("/v2/management/orderstate", json=order_state_1)
            order_state_2 = OrderState(status="to_accept", order_id=2)
            for _ in range(200):
                c.post("/v2/management/orderstate", json=order_state_2)

            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 50)

            response = c.get("/v2/management/orderstate/2?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 50)

            response = c.get("/v2/management/orderstate?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 100)


class Test_Deleting_Order_States_When_Deleting_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        other_order = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order)
            c.post("/v2/management/order", json=other_order)

    def test_deleting_order_deletes_all_its_states(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        other_order_state = OrderState(status="canceled", order_id=2)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=order_state_1)
            c.post("/v2/management/orderstate", json=order_state_2)
            c.post("/v2/management/orderstate", json=other_order_state)
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(len(response.json), 3)

            c.delete("/v2/management/order/1/1")
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 404)

            response = c.get("/v2/management/orderstate?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Accepting_Order_States_After_Receiving_State_With_Final_Status(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(
            priority="high",
            user_id=1,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone={},
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order)

    def test_sending_single_order_state_after_DONE_status_has_been_received_yield_403_code(self):
        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        next_state_1 = OrderState(status=OrderStatus.TO_ACCEPT, order_id=1)
        next_state_2 = OrderState(status=OrderStatus.ACCEPTED, order_id=1)
        next_state_3 = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        next_state_4 = OrderState(status=OrderStatus.CANCELED, order_id=1)
        next_state_5 = OrderState(status=OrderStatus.DONE, order_id=1)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/orderstate", json=done_state)
            self.assertEqual(response.status_code, 200)

            for next_state in [next_state_1, next_state_2, next_state_3, next_state_4, next_state_5]:
                response = c.post("/v2/management/orderstate", json=next_state)
                self.assertEqual(response.status_code, 403)

            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.DONE)

    def test_sending_single_order_state_after_CANCELED_status_has_been_received_yield_403_code(self):
        done_state = OrderState(status=OrderStatus.CANCELED, order_id=1)
        next_state_1 = OrderState(status=OrderStatus.TO_ACCEPT, order_id=1)
        next_state_2 = OrderState(status=OrderStatus.ACCEPTED, order_id=1)
        next_state_3 = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        next_state_4 = OrderState(status=OrderStatus.DONE, order_id=1)
        next_state_5 = OrderState(status=OrderStatus.CANCELED, order_id=1)
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/orderstate", json=done_state)
            self.assertEqual(response.status_code, 200)

            for next_state in [next_state_1, next_state_2, next_state_3, next_state_4, next_state_5]:
                response = c.post("/v2/management/orderstate", json=next_state)
                self.assertEqual(response.status_code, 403)

            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.CANCELED)


class Test_Recongnizing_Done_And_Canceled_Orders_After_Restarting_Application(unittest.TestCase):

    def test_done_state(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        done_state = OrderState(status=OrderStatus.DONE, order_id=1)
        next_state = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order)
            c.post("/v2/management/orderstate", json=done_state)

        self.app = _app.get_test_app()
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.DONE)
            response = c.post("/v2/management/orderstate", json=next_state)
            self.assertEqual(response.status_code, 403)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.DONE)

    def test_canceled_state(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        car = Car(name="car1", platform_hw_id=1, car_admin_phone={})
        order = Order(user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        canceled_state = OrderState(status=OrderStatus.CANCELED, order_id=1)
        next_state = OrderState(status=OrderStatus.IN_PROGRESS, order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=car)
            c.post("/v2/management/order", json=order)
            c.post("/v2/management/orderstate", json=canceled_state)

        self.app = _app.get_test_app()
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.CANCELED)
            response = c.post("/v2/management/orderstate", json=next_state)
            self.assertEqual(response.status_code, 403)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.json[-1].get("status"), OrderStatus.CANCELED)


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no coverage
