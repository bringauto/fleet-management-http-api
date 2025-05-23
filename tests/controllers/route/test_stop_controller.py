import os
import unittest

import fleet_management_api.database.connection as _connection
import fleet_management_api.models as _models
import fleet_management_api.app as _app
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.models import Stop, GNSSPosition, Tenant
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.api_impl.auth_controller import (
    generate_test_keys,
    set_auth_params,
    get_test_public_key,
    clear_test_keys,
    clear_auth_params,
)

from tests._utils.setup_utils import create_platform_hws, create_stops, create_route
from tests._utils.constants import TEST_TENANT_NAME
import tests._utils.api_test as api_test


class Test_Creating_Stops(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True).app

    def test_creating_stops(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop_1 = _models.Stop(
            id=1,
            name="stop_1",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        stop_2 = _models.Stop(
            id=2,
            name="stop_2",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
            is_auto_stop=True,
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/stop", json=[stop_1])
            self.assertEqual(response.status_code, 200)
            response = c.post("/v2/management/stop", json=[stop_2])
            self.assertEqual(response.status_code, 200)

    def test_creating_stop_with_identical_name_yields_code_400(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop_1 = _models.Stop(
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        stop_2 = _models.Stop(
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/stop", json=[stop_1])
            self.assertEqual(response.status_code, 200)
            response = c.post("/v2/management/stop", json=[stop_2])
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_invalid_json_yields_code_400(self):
        with self.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/stop", json="invalid json")
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_incomplete_data_yields_code_400(self):
        with self.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/stop", json={})
            self.assertEqual(response.status_code, 400)
            response = c.post("/v2/management/stop", json={"id": 1, "name": "stop_1"})
            self.assertEqual(response.status_code, 400)


class Test_Identical_Stop_Names(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")
        self.app = _app.get_test_app(
            "testAPIKey", accessible_tenants=["tenant_1", "tenant_2"], use_previous=True
        )
        with self.app.app.test_client() as client:
            client.post(
                "v2/management/tenant?api_key=testAPIKey",
                json=[Tenant(name="tenant_1"), Tenant(name="tenant_2")],
            )

    def test_creating_two_stops_ith_identical_names_under_the_same_tenant_returns_error(
        self,
    ) -> None:

        position = GNSSPosition(latitude=1, longitude=1, altitude=1)
        with self.app.app.test_client() as client:
            stop_a = Stop(name="Stop", position=position)
            stop_b = Stop(name="Stop", position=position)
            client.set_cookie("", "tenant", "tenant_1")
            client.post("/v2/management/stop?api_key=testAPIKey", json=[stop_a])
            response = client.post("/v2/management/stop?api_key=testAPIKey", json=[stop_b])
            self.assertEqual(response.status_code, 400)

    def test_creating_two_platform_hw_ith_identical_names_under_different_tenants_returns_success(
        self,
    ):
        position = GNSSPosition(latitude=1, longitude=1, altitude=1)
        with self.app.app.test_client() as client:
            stop_a = Stop(name="Stop", position=position)
            stop_b = Stop(name="Stop", position=position)
            client.set_cookie("", "tenant", "tenant_1")
            client.post("/v2/management/stop?api_key=testAPIKey", json=[stop_a])
            client.set_cookie("", "tenant", "tenant_2")
            response = client.post("/v2/management/stop?api_key=testAPIKey", json=[stop_b])
            self.assertEqual(response.status_code, 200)
            client.set_cookie("", "tenant", "")
            response = client.get("/v2/management/stop?api_key=testAPIKey")
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["name"], "Stop")
            self.assertEqual(response.json[1]["name"], "Stop")

    def tearDown(self):
        clear_test_keys()
        clear_auth_params()


class Test_Adding_Stop_Using_Example_From_Spec(unittest.TestCase):
    def test_adding_stop_using_example_from_spec(self):
        _connection.set_connection_source_test()
        app = _app.get_test_app(use_previous=True).app
        with app.test_client(TEST_TENANT_NAME) as c:
            example = c.get("/v2/management/openapi.json").json["components"]["schemas"]["Stop"][
                "example"
            ]
            response = c.post("/v2/management/stop", json=[example])
            self.assertEqual(response.status_code, 200)


class Test_Retrieving_All_Stops(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True).app

    def test_retrieving_all_stops_without_creating_any_yields_code_200_and_empty_list(
        self,
    ):
        with self.app.test_client(TEST_TENANT_NAME) as client:
            response = client.get("/v2/management/stop")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_retrieving_sent_stops(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop_1 = _models.Stop(
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        stop_2 = _models.Stop(
            name="stop_Y",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/stop", json=[stop_1, stop_2])
            response = c.get("/v2/management/stop")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Retrieving_Single_Stop(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True).app

    def test_retrieving_single_existing_stop(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop_1 = _models.Stop(
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        stop_2 = _models.Stop(
            name="stop_Y",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/stop", json=[stop_1, stop_2])

            response = c.get("/v2/management/stop/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], stop_1.name)

            response = c.get("/v2/management/stop/2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], stop_2.name)

    def test_retrieving_single_non_existing_stop_yields_code_404(self):
        with self.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/stop/1")
            self.assertEqual(response.status_code, 404)


class Test_Deleting_Stop(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True).app

    def test_deleting_single_existing_stop(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop = _models.Stop(
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/stop", json=[stop])
            response = c.get("/v2/management/stop")

            self.assertEqual(len(response.json), 1)

            response = c.delete("/v2/management/stop/1")
            self.assertEqual(response.status_code, 200)

            response = c.get("/v2/management/stop")
            self.assertEqual(len(response.json), 0)

    def test_deleting_single_non_existing_stop_yields_code_404(self):
        with self.app.test_client(TEST_TENANT_NAME) as c:
            response = c.delete("/v2/management/stop/1")
            self.assertEqual(response.status_code, 404)


class Test_Updating_Stop(unittest.TestCase):
    def setUp(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True).app
        _db_access.add_without_tenant(_db_models.TenantDB(name=TEST_TENANT_NAME))

    def test_updating_single_existing_stop(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop = _models.Stop(
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/stop", json=[stop])
            stop.name = "stop_Y"
            stop.id = 1
            response = c.put("/v2/management/stop", json=[stop])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/stop/1")
            self.assertEqual(response.json["name"], "stop_Y")

    def test_updating_nonexisting_stop_yields_code_404(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop = _models.Stop(
            id=116516556165,
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            response = c.put("/v2/management/stop", json=[stop])
            self.assertEqual(response.status_code, 404)

    def test_updating_stop_with_incomplete_data_yields_code_400(self):
        position = _models.GNSSPosition(latitude=49, longitude=16, altitude=50)
        stop = _models.Stop(
            name="stop_X",
            position=position,
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        with self.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/stop", json=[stop])

            response = c.put("/v2/management/stop", json=[{"name": "stop_Y"}])
            self.assertEqual(response.status_code, 400)


class Test_Stop_Cannot_Be_Deleted_If_Assigned_To_Order(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app(use_previous=True)
        self.stop = _models.Stop(
            id=1,
            name="stop_X",
            position=_models.GNSSPosition(latitude=49, longitude=16, altitude=50),
            notification_phone=_models.MobilePhone(phone="123456789"),
        )
        create_platform_hws(self.app, 2)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))
        self.car = _models.Car(
            id=1,
            platform_hw_id=2,
            name="test_car",
            car_admin_phone=_models.MobilePhone(phone="123456789"),
        )
        self.order = _models.Order(
            id=1,
            priority="normal",
            is_visible=True,
            car_id=1,
            target_stop_id=1,
            stop_route_id=1,
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[self.car])
            c.post("/v2/management/order", json=[self.order])

    def test_stop_cannot_be_deleted_if_referenced_by_some_order(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/stop", json=[self.stop])

            response = c.delete("/v2/management/stop/1")
            self.assertEqual(response.status_code, 400)

            c.delete("/v2/management/order/1/1")
            c.delete("/v2/management/route/1")
            response = c.delete("/v2/management/stop/1")
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no cover
