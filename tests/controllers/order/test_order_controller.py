import unittest
import sys
from unittest.mock import patch, Mock
import os

sys.path.append(".")

import fleet_management_api.database.connection as _connection
from fleet_management_api.models import Order, Car, MobilePhone, OrderState, OrderStatus
import fleet_management_api.app as _app
from tests.utils.setup_utils import create_platform_hws, create_stops, create_route
from fleet_management_api.api_impl.controllers.order import (
    clear_active_orders,
    clear_inactive_orders,
    set_max_n_of_active_orders,
)


class Test_Sending_Order(unittest.TestCase):
    def setUp(self) -> None:

        _connection.set_connection_source_test("test.db")
        clear_active_orders()
        clear_inactive_orders()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 7)
        create_route(self.app, stop_ids=(2, 4, 6))
        self.car = Car(
            name="test_car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car])

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_sending_order_to_exising_car(self, mock_timestamp: Mock):
        mock_timestamp.return_value = 1000
        order = Order(
            is_visible=True,
            timestamp=1000,
            car_id=1,
            target_stop_id=2,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/order", json=[order])
            self.assertEqual(response.status_code, 200)
            order.id = 1
            assert response.json is not None
            self.assertEqual(response.json[0]["id"], order.id)
            self.assertEqual(response.json[0]["timestamp"], order.timestamp)
            self.assertEqual(response.json[0]["carId"], order.car_id)
            self.assertEqual(response.json[0]["targetStopId"], order.target_stop_id)
            self.assertEqual(response.json[0]["stopRouteId"], order.stop_route_id)
            self.assertEqual(
                response.json[0]["notificationPhone"]["phone"], order.notification_phone.phone
            )
            self.assertEqual(response.json[0]["lastState"]["status"], "to_accept")

    def test_sending_order_to_non_exising_car_yields_code_404(self):
        nonexistent_car_id = 6546515
        order = Order(
            is_visible=True,
            car_id=nonexistent_car_id,
            target_stop_id=2,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/order", json=[order])
            self.assertEqual(response.status_code, 404)

    def test_sending_order_referencing_nonexistent_stop_yields_code_404(self):
        order = Order(
            is_visible=True,
            car_id=1,
            target_stop_id=16316516,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/order", json=[order])
            self.assertEqual(response.status_code, 404)

    def test_specifying_route_not_containing_the_target_stop_yields_code_400(self):
        order = Order(
            is_visible=True,
            car_id=1,
            target_stop_id=3,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/order", json=[order])
            self.assertEqual(response.status_code, 400)

    def test_sending_incomplete_order_data_yields_code_400(self):
        incomplete_order_dict = {}
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/order", json=[incomplete_order_dict])
            self.assertEqual(response.status_code, 400)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Creating_Order_From_Example_In_Spec(unittest.TestCase):
    def test_creating_order_from_example_in_spec(self):
        _connection.set_connection_source_test("test.db")
        clear_active_orders()
        clear_inactive_orders()
        app = _app.get_test_app()
        create_platform_hws(app)
        create_stops(app, 1)
        create_route(app, stop_ids=(1,))
        with app.app.test_client() as c:
            example = c.get("/v2/management/openapi.json").json["components"]["schemas"]["Order"][
                "example"
            ]
            car = Car(
                id=example["carId"],
                name="Test Car",
                platform_hw_id=1,
                car_admin_phone=MobilePhone(phone="1234567890"),
            )
            c.post("/v2/management/car", json=[car])

            response = c.post("/v2/management/order", json=[example])
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_No_Orders(unittest.TestCase):

    def setUp(self) -> None:

        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app()

    def test_retrieving_all_orders_when_no_orders_exist_yields_code_200(self):
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order")
            self.assertEqual(response.status_code, 200)
            self.assertListEqual(response.json, [])

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_All_Retrieving_Orders(unittest.TestCase):
    def setUp(self) -> None:

        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        create_stops(self.app, 7)
        create_route(self.app, stop_ids=(2, 4, 6))
        set_max_n_of_active_orders(5)
        self.car_1 = Car(
            name="test_car_1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        self.car_2 = Car(
            name="test_car_2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="1234567890")
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/car", json=[self.car_1])
            assert response.json is not None
            self.car_1.id = response.json[0]["id"]
            response = c.post("/v2/management/car", json=[self.car_2])
            assert response.json is not None
            self.car_2.id = response.json[0]["id"]

        self.order_1 = Order(
            is_visible=True,
            car_id=1,
            target_stop_id=2,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        self.order_2 = Order(
            is_visible=True,
            car_id=2,
            target_stop_id=2,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        with self.app.app.test_client() as c:
            c.post(
                "/v2/management/order",
                json=[self.order_1, self.order_1, self.order_2, self.order_2, self.order_2],
            )

    def test_retrieving_all_orders_when_some_orders_exist_yields_code_200_and_list_of_orders(self):
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 5)

    def test_retrieving_all_orders_for_car_when_some_orders_exist_yields_list_of_orders_assigned_to_the_car(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order/{self.car_1.id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            response = c.get(f"/v2/management/order/{self.car_2.id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)

    def test_retrieving_nonexistent_order(self):
        nonexistent_order_id = 651651651
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order/12/{nonexistent_order_id}")
            self.assertEqual(response.status_code, 404)

    def test_retrieving_orders_for_nonexistent_car(self):
        nonexistent_car_id = 651651651
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order/{nonexistent_car_id}")
            self.assertEqual(response.status_code, 404)

    def test_retrieving_all_orders_when_some_orders_exist_yields_code_200(self):
        order = Order(
            is_visible=True,
            car_id=1,
            target_stop_id=2,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            response = c.get(f"/v2/management/order")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Order.from_dict(response.json[0]).target_stop_id, order.target_stop_id)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Retrieving_Single_Order_From_The_Database(unittest.TestCase):
    def setUp(self):

        self.maxDiff = None
        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 7)
        create_route(self.app, stop_ids=(2, 4, 6))
        self.car = Car(
            name="test_car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car])

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_retrieving_existing_order(self, mock_timestamp: Mock):
        mock_timestamp.return_value = 1000
        order = Order(
            is_visible=True,
            timestamp=1000,
            car_id=1,
            target_stop_id=4,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/order", json=[order])
            response = c.get(f"/v2/management/order/1/1")
            self.assertEqual(response.status_code, 200)
            order.id = 1
            order.last_state = OrderState(
                id=1, status=OrderStatus.TO_ACCEPT, order_id=1, timestamp=1000
            )
            self.assertEqual(Order.from_dict(response.json).id, order.id)
            self.assertEqual(Order.from_dict(response.json).last_state, order.last_state)
            self.assertEqual(Order.from_dict(response.json).target_stop_id, order.target_stop_id)
            self.assertEqual(Order.from_dict(response.json).stop_route_id, order.stop_route_id)

    def test_retrieving_non_existing_order_yields_code_404(self):
        nonexistent_order_id = 65169861848
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order/{nonexistent_order_id}")
            self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Deleting_Order(unittest.TestCase):
    def setUp(self):

        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        create_stops(self.app, 7)
        create_route(self.app, stop_ids=(2, 4, 6))
        self.car = Car(
            name="test_car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car])
            self.order = Order(
                is_visible=True,
                car_id=1,
                target_stop_id=6,
                stop_route_id=1,
                notification_phone=MobilePhone(phone="1234567890"),
            )
            c.post("/v2/management/order", json=[self.order])

    def test_deleting_existing_order(self):
        with self.app.app.test_client() as c:
            response = c.delete(f"/v2/management/order/1/1")
            self.assertEqual(response.status_code, 200)
            response = c.get(f"/v2/management/order")
            self.assertEqual(response.json, [])

    def test_deleting_nonexistent_order_yields_code_404(self):
        nonexistent_order_id = 651651651
        with self.app.app.test_client() as c:
            response = c.delete(f"/v2/management/order/1/{nonexistent_order_id}")
            self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


class Test_Retrieving_Orders_By_Creation_Timestamp(unittest.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mock_timestamp: Mock) -> None:

        _connection.set_connection_source_test("test.db")
        self.app = _app.get_test_app()
        mock_timestamp.return_value = 0
        create_platform_hws(self.app)
        create_stops(self.app, 2)
        create_route(self.app, stop_ids=(1, 2))
        self.car = Car(
            name="test_car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="1234567890")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car])

        self.order_1 = Order(
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="1234567890"),
        )
        self.order_2 = Order(
            is_visible=True,
            car_id=1,
            target_stop_id=2,
            stop_route_id=1,
            notification_phone=MobilePhone(phone="4444444444"),
        )
        with self.app.app.test_client() as c:
            mock_timestamp.return_value = 1000
            c.post("/v2/management/order", json=[self.order_1])
            mock_timestamp.return_value = 2000
            c.post("/v2/management/order", json=[self.order_2])

    def test_setting_since_to_zero_returns_all_orders(self) -> None:
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order?since=0")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["timestamp"], 1000)

    def test_setting_since_to_time_after_some_status_returns_only_statuses_after_that(self) -> None:
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order?since=1001")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["timestamp"], 2000)

    def test_filtering_out_all_statuses(self) -> None:
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/order?since=2001")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 0)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test.db"):
            os.remove("test.db")


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no coverage
