import unittest

import fleet_management_api.app as _app
from fleet_management_api.database.connection import set_connection_source_test
from fleet_management_api.models import (
    Route,
    Order,
    Car,
    PlatformHW,
    Stop,
    GNSSPosition,
    MobilePhone,
)
from fleet_management_api.api_impl.auth_controller import (
    generate_test_keys,
    set_auth_params,
    clear_auth_params,
    clear_test_keys,
    get_test_public_key,
)

from tests._utils.setup_utils import create_stops, create_route
from tests._utils.constants import TEST_TENANT_NAME
import tests._utils.api_test as api_test


class Test_Creating_Route(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)

    def test_creating_route(self):
        route = Route(name="test_route")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/route", json=[route])
            self.assertEqual(response.status_code, 200)

    def test_creating_route_with_already_taken_name_returns_code_400(self):
        route_1 = Route(name="test_route")
        route_2 = Route(name="test_route")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/route", json=[route_1])
            self.assertEqual(response.status_code, 200)
            response = c.post("/v2/management/route", json=[route_2])
            self.assertEqual(response.status_code, 400)

    def test_creating_route_with_missing_name_returns_code_400(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/route", json=[{"id": 1}])
            self.assertEqual(response.status_code, 400)


class Test_Identical_Route_Names(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")
        self.app = _app.get_test_app(
            "testAPIKey", accessible_tenants=["tenant_1", "tenant_2"], use_previous=True
        )
        with self.app.app.test_client() as client:
            position = GNSSPosition(latitude=1, longitude=1, altitude=1)
            client.set_cookie("", "tenant", "tenant_1")
            response_a = client.post(
                "/v2/management/stop?api_key=testAPIKey",
                json=[Stop(name="stop_a", position=position)],
            )
            self.assertEqual(response_a.status_code, 200)
            response_b = client.post(
                "/v2/management/stop?api_key=testAPIKey",
                json=[Stop(name="stop_b", position=position)],
            )
            self.assertEqual(response_b.status_code, 200)
            client.set_cookie("", "tenant", "tenant_2")
            response_c = client.post(
                "/v2/management/stop?api_key=testAPIKey",
                json=[Stop(name="stop_c", position=position)],
            )
            self.assertEqual(response_c.status_code, 200)

    def test_creating_two_routes_ith_identical_names_under_the_same_tenant_returns_error(
        self,
    ) -> None:

        with self.app.app.test_client() as client:
            route_1 = Route(name="Route", stop_ids=[1])
            route_2 = Route(name="Route", stop_ids=[2])
            client.set_cookie("", "tenant", "tenant_1")
            client.post("/v2/management/route?api_key=testAPIKey", json=[route_1])
            response = client.post("/v2/management/route?api_key=testAPIKey", json=[route_2])
            self.assertEqual(response.status_code, 400)

    def test_creating_two_routes_with_identical_names_under_different_tenants_returns_success(
        self,
    ):
        with self.app.app.test_client() as client:
            route_1 = Route(name="Route", stop_ids=[1])
            route_2 = Route(name="Route", stop_ids=[3])
            client.set_cookie("", "tenant", "tenant_1")
            client.post("/v2/management/route?api_key=testAPIKey", json=[route_1])
            client.set_cookie("", "tenant", "tenant_2")
            response = client.post("/v2/management/route?api_key=testAPIKey", json=[route_2])
            self.assertEqual(response.status_code, 200)

    def tearDown(self):
        clear_test_keys()
        clear_auth_params()


class Test_Adding_Route_Using_Example_From_Spec(unittest.TestCase):
    def test_adding_state_using_example_from_spec(self):
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            example = c.get("/v2/management/openapi.json").json["components"]["schemas"]["Route"][
                "example"
            ]
            # remove stop ids (these stops are not defined for this test)
            example["stopIds"] = []
            response = c.post("/v2/management/route", json=[example])
            self.assertEqual(response.status_code, 200)


class Test_Getting_All_Routes(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)

    def test_retrieving_existing_routes(self):
        route_1 = Route(name="test_route_1")
        route_2 = Route(name="test_route_2")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/route", json=[route_1, route_2])
            response = c.get("/v2/management/route")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_retrieving_routes_when_route_exists_yields_empty_list(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/route")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])


class Test_Getting_Single_Route(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        self.route_1 = Route(name="test_route_1")
        self.route_2 = Route(name="test_route_2")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/route", json=[self.route_1, self.route_2])

    def test_retrieving_existing_route(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/route/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], self.route_1.name)

            response = c.get("/v2/management/route/2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], self.route_2.name)

    def test_retrieving_nonexistent_route_yields_code_404(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/route/999")
            self.assertEqual(response.status_code, 404)


class Test_Retrieving_Route_Stops(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        stop_1 = Stop(name="stop_1", position=GNSSPosition(latitude=1, longitude=1, altitude=1))
        stop_2 = Stop(name="stop_2", position=GNSSPosition(latitude=2, longitude=2, altitude=2))
        stop_3 = Stop(name="stop_3", position=GNSSPosition(latitude=3, longitude=3, altitude=3))
        self.route_1 = Route(name="test_route_1", stop_ids=[1, 2])
        self.route_2 = Route(name="test_route_2", stop_ids=[2, 3])
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/stop", json=[stop_1, stop_2, stop_3])
            c.post("/v2/management/route", json=[self.route_1, self.route_2])

    def test_retrieving_existing_route_stops(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/route/1")
            self.assertEqual(response.status_code, 200)
            route_stop_ids = response.json["stopIds"]
            self.assertEqual(len(route_stop_ids), 2)


class Test_Deleting_Route(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        create_stops(self.app, 1)
        create_route(self.app, stop_ids=(1,))

    def test_deleting_an_existing_Route(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.delete("/v2/management/route/1")
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/route/1")
            self.assertEqual(response.status_code, 404)

    def test_deleting_a_nonexistent_Route_yields_code_404(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.delete("/v2/management/route/999")
            self.assertEqual(response.status_code, 404)

    def test_route_cannot_be_deleted_if_some_order_references_it(self):
        platform_hw = PlatformHW(name="test_platform_hw_1")
        car = Car(
            id=1,
            name="test_car_1",
            platform_hw_id=1,
            car_admin_phone=MobilePhone(phone="123456789"),
        )
        order = Order(id=1, stop_route_id=1, target_stop_id=1, is_visible=True, car_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/platformhw", json=[platform_hw])
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])
            response = c.delete("/v2/management/route/1")
            self.assertEqual(response.status_code, 400)
            response = c.get("/v2/management/route/1")
            self.assertEqual(response.status_code, 200)


class Test_Updating_Route(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        self.route = Route(name="test_route_1")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/route", json=[self.route])

    def test_updating_existing_route_yiels_code_200(self):
        updated_route = Route(id=1, name="better_name")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.put("/v2/management/route", json=[updated_route])
            self.assertEqual(response.status_code, 200)

            response = c.get("/v2/management/route/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], "better_name")

    def test_updating_nonexistent_route_yields_code_404(self):
        updated_route = Route(name="better_name")
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.put("/v2/management/route", json=[updated_route])
            self.assertEqual(response.status_code, 404)

    def test_updating_existing_route_with_incomplete_data_yields_code_400(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.put("/v2/management/route", json=[{"id": 1}])
            self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no coverage
