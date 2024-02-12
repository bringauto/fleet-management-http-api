import unittest
import sys

sys.path.append(".")

import fleet_management_api.app as _app
from fleet_management_api.models import OrderState, Order, Car
import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_models as _db_models
from tests.utils.setup_utils import create_platform_hws, create_stops


class Test_Adding_State_Of_Existing_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
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
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
        with self.app.app.test_client() as c:
            example = c.get("/v2/management/openapi.json").json["components"][
                "schemas"
            ]["OrderState"]["example"]

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

    def test_getting_all_order_states_when_state_has_been_created_yields_empty_list(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_all_order_states(self):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=1)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=order_state_1)
            c.post("/v2/management/orderstate", json=order_state_2)
            response = c.get("/v2/management/orderstate?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Getting_Order_State_For_Given_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
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

    def test_getting_order_state_for_existing_order_before_any_state_has_been_created_yields_empty_list(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_order_state_for_existing_order_after_state_has_been_created_yields_list_containing_the_one_state(
        self,
    ):
        order_state_1 = OrderState(status="to_accept", order_id=1)
        order_state_2 = OrderState(status="canceled", order_id=2)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=order_state_1)
            c.post("/v2/management/orderstate", json=order_state_2)
            response = c.get("/v2/management/orderstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id"], 1)

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
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["id"], 1)
            self.assertEqual(response.json[1]["id"], 2)


class Test_Adding_Order_State_Makes_Order_To_Be_Listed_As_Updated(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
        car = Car(id=1, name="car1", platform_hw_id=1, car_admin_phone={})
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

    def test_adding_state_to_existing_order_makes_the_order_to_appear_as_updated(self):
        order_state = OrderState(status="to_accept", order_id=1)
        with self.app.app.test_client() as c:
            c.get("/v2/management/order/wait/1")
            c.post("/v2/management/orderstate", json=order_state)
            response = c.get("/v2/management/order/wait/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)


class Test_Maximum_Number_Of_States_Stored(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
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
        self.max_n = _db_models.OrderStateDBModel.max_n_of_stored_states()

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(
        self,
    ):
        with self.app.app.test_client() as c:
            oldest_state = OrderState(status="to_accept", order_id=1)
            c.post("/v2/management/orderstate", json=oldest_state)
            for i in range(1, self.max_n - 1):
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


class Test_Deleting_Order_States_When_Deleting_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 1)
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
            self.assertEqual(len(response.json), 2)

            c.delete("/v2/management/order/1")
            response = c.get("/v2/management/orderstate/1?since=0")
            self.assertEqual(response.status_code, 404)

            response = c.get("/v2/management/orderstate?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=True)  # pragma: no coverage
