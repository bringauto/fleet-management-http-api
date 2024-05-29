import unittest
import sys
import os

sys.path.append(".")


import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import Car, Order, OrderState, MobilePhone, GNSSPosition
from tests.utils.setup_utils import create_platform_hws, create_stops, create_route


POSITION = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)


class Test_Order_Is_Returned_With_Its_Last_State(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        create_stops(self.app, 2)
        create_route(self.app, stop_ids=(1, 2))
        self.car = Car(
            platform_hw_id=1,
            name="car1",
            car_admin_phone=MobilePhone(phone="123456789")
        )
        self.order_1 = Order(
            user_id=1,
            target_stop_id=1,
            stop_route_id=1,
            car_id=1,
            notification_phone=MobilePhone(phone="123456789")
        )
        self.order_2 = Order(
            user_id=1,
            target_stop_id=2,
            stop_route_id=1,
            car_id=1,
            notification_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/car", json=[self.car])
            assert response.json is not None
            self.car = Car.from_dict(response.json[0])
            response = c.post("/v2/management/order", json=[self.order_1, self.order_2])
            assert response.json is not None and response.json != []
            self.order_1 = Order.from_dict(response.json[0])
            self.order_2 = Order.from_dict(response.json[1])

    def test_order_is_returned_with_its_last_state(self):
        state_1 = OrderState(status="to_accept", order_id=self.order_1.id)
        state_2 = OrderState(status="in_progress", order_id=self.order_1.id)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=[state_1])
            c.post("/v2/management/orderstate", json=[state_2])

        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order/{self.car.id}/{self.order_1.id}")
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.json["lastState"]["status"], state_2.status)

    def test_car_orders_are_returned_with_their_last_states(self):
        state_1 = OrderState(status="to_accept", order_id=self.order_1.id)
        state_2 = OrderState(status="done", order_id=self.order_1.id)
        state_3 = OrderState(status="accepted", order_id=self.order_2.id)
        state_4 = OrderState(status="in_progress", order_id=self.order_2.id)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=[state_1, state_2, state_3, state_4])
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order/{self.car.id}")
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["lastState"]["status"], state_2.status)
            self.assertEqual(response.json[1]["lastState"]["status"], state_4.status)

    def test_all_orders_are_returned_with_their_last_states(self):
        state_1 = OrderState(status="to_accept", order_id=self.order_1.id)
        state_2 = OrderState(status="done", order_id=self.order_1.id)
        state_3 = OrderState(status="accepted", order_id=self.order_2.id)
        state_4 = OrderState(status="in_progress", order_id=self.order_2.id)
        with self.app.app.test_client() as c:
            c.post("/v2/management/orderstate", json=[state_1, state_2, state_3, state_4])
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order")
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["lastState"]["status"], state_2.status)
            self.assertEqual(response.json[1]["lastState"]["status"], state_4.status)

    def tearDown(self) -> None:
        if os.path.isfile("test.db"):
            os.remove("test.db")


if __name__=='__main__':  # pragma: no cover
    unittest.main()