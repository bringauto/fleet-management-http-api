import unittest

from fleet_management_api.app import get_app
from fleet_management_api.models import OrderState, Order, Car
import fleet_management_api.database.connection as connection


class Test_Adding_State_Of_Existing_Order(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        self.app = get_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order)

    def test_adding_state_to_existing_order(self):
        order_state = OrderState(id=1, status="to_accept", order_id=12)
        with self.app.test_client() as c:
            response = c.post('/v1/orderstate', json=order_state)
            self.assertEqual(response.status_code, 200)

    def test_adding_state_to_none_existing_order_returns_code_404(self):
        order_state = OrderState(id=1, status="to_accept", order_id=4651684651)
        with self.app.test_client() as c:
            response = c.post('/v1/orderstate', json=order_state)
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_state_returns_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/orderstate', json={})
            self.assertEqual(response.status_code, 400)

    def test_sending_repeatedly_state_with_identical_id_returns_code_400(self):
        order_state = OrderState(id=1, status="to_accept", order_id=12)
        with self.app.test_client() as c:
            response = c.post('/v1/orderstate', json=order_state)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/orderstate', json=order_state)
            self.assertEqual(response.status_code, 400)


class Test_Adding_State_Using_Example_From_Spec(unittest.TestCase):

    def test_adding_state_using_example_from_spec(self):
        connection.set_test_connection_source()
        self.app = get_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        with self.app.test_client() as c:
            example = c.get('/v1/openapi.json').json["components"]["schemas"]["OrderState"]["example"]

            order = Order(id=example["orderId"], priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order)

            response = c.post('/v1/orderstate', json=example)
            self.assertEqual(response.status_code, 200)


class Test_Getting_All_Order_States_For_Given_Order(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        self.app = get_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order)

    def test_getting_all_order_states_when_state_has_been_created_yields_empty_list(self):
        with self.app.test_client() as c:
            response = c.get('/v1/orderstate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_all_order_states(self):
        order_state_1 = OrderState(id=3, status="to_accept", order_id=12)
        order_state_2 = OrderState(id=7, status="canceled", order_id=12)
        with self.app.test_client() as c:
            c.post('/v1/orderstate', json=order_state_1)
            c.post('/v1/orderstate', json=order_state_2)
            response = c.get('/v1/orderstate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Getting_Order_State_For_Given_Order(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        self.app = get_app().app
        car = Car(id=1, name="car1", platform_id=1, car_admin_phone={})
        order_1 = Order(id=12, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        order_2 = Order(id=13, priority="high", user_id=1, car_id=1, target_stop_id=1, stop_route_id=1, notification_phone={})
        with self.app.test_client() as c:
            c.post('/v1/car', json=car)
            c.post('/v1/order', json=order_1)
            c.post('/v1/order', json=order_2)

    def test_getting_order_state_for_existing_order_before_any_state_has_been_created_yields_empty_list(self):
        with self.app.test_client() as c:
            response = c.get('/v1/orderstate/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_order_state_for_existing_order_after_state_has_been_created_yields_list_with_state(self):
        order_state_1 = OrderState(id=3, status="to_accept", order_id=12)
        order_state_2 = OrderState(id=7, status="canceled", order_id=13)
        with self.app.test_client() as c:
            c.post('/v1/orderstate', json=order_state_1)
            c.post('/v1/orderstate', json=order_state_2)
            response = c.get('/v1/orderstate/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id"], 3)

    def test_getting_order_state_for_nonexisting_order_returns_code_404(self):
        with self.app.test_client() as c:
            response = c.get('/v1/orderstate/4651684651')
            self.assertEqual(response.status_code, 404)

    def test_getting_last_order_state(self):
        order_state_1 = OrderState(id=3, status="to_accept", order_id=12)
        order_state_2 = OrderState(id=7, status="canceled", order_id=12)
        with self.app.test_client() as c:
            c.post('/v1/orderstate', json=order_state_1)
            c.post('/v1/orderstate', json=order_state_2)
            response = c.get('/v1/orderstate/12?allAvailable=false')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id"], 7)

    def test_getting_all_order_states(self):
        order_state_1 = OrderState(id=3, status="to_accept", order_id=12)
        order_state_2 = OrderState(id=7, status="canceled", order_id=12)
        with self.app.test_client() as c:
            c.post('/v1/orderstate', json=order_state_1)
            c.post('/v1/orderstate', json=order_state_2)
            response = c.get('/v1/orderstate/12?allAvailable=true')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["id"], 3)
            self.assertEqual(response.json[1]["id"], 7)


if __name__ == '__main__':
    unittest.main() # pragma: no coverage