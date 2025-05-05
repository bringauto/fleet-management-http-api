import unittest
from fleet_management_api.models import Car, PlatformHW, Order, MobilePhone
import fleet_management_api.app as _app
from fleet_management_api.api_impl.tenants import decode_jwt_token
from fleet_management_api.database.db_access import delete
from fleet_management_api.database.db_models import CarStateDB
from fleet_management_api.logs import LOGGER_NAME
from fleet_management_api.api_impl.auth_controller import (
    generate_test_keys,
    set_auth_params,
    clear_auth_params,
    clear_test_keys,
    get_test_public_key,
    get_public_key,
)

from tests._utils.constants import TEST_TENANT_NAME
from tests._utils.setup_utils import create_stops, create_platform_hws, create_route

import tests._utils.api_test as api_test
from tests._utils.setup_utils import TenantFromTokenMock


PHONE = MobilePhone(phone="123456789")


class Test_Creating_And_Getting_Cars(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        self.app.app.def_accessible_tenants(TEST_TENANT_NAME)
        create_platform_hws(self.app, 2)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))

    def test_cars_list_is_initially_available_and_empty(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/car")
            self.assertEqual(response.json, [])
            self.assertEqual(response.status_code, 200)

    def test_creating_car_without_existing_platform_hw_yields_404_error_code(self):
        car = Car(
            name="Test Car",
            platform_hw_id=216465168,
            under_test=False,
            car_admin_phone=PHONE,
        )
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post(
                "/v2/management/car",
                json=[car],
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 404)

    def test_car_with_default_route_id_pointing_to_nonexistent_route_yields_404_error_code(self):
        nonexistent_route_id = 165168486
        car = Car(
            name="Test Car",
            platform_hw_id=1,
            default_route_id=nonexistent_route_id,
            car_admin_phone=PHONE,
        )
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/car", json=[car], content_type="application/json")
            self.assertEqual(response.status_code, 404)

    def test_deleting_cars_default_route_sets_the_default_route_id_of_the_car_to_none(self):
        car = Car(
            name="Test Car",
            platform_hw_id=1,
            default_route_id=1,
            car_admin_phone=PHONE,
        )
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car], content_type="application/json")

            response = c.get("/v2/management/car/1")
            self.assertEqual(response.json["defaultRouteId"], 1)

            c.delete("/v2/management/route/1")
            response = c.get("/v2/management/car/1")
            self.assertTrue("defaultRouteId" not in response.json)

    def test_creating_and_retrieving_a_car(self):
        car = Car(
            name="Test Car",
            platform_hw_id=1,
            default_route_id=1,
            under_test=False,
            car_admin_phone=PHONE,
        )
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/car", json=[car], content_type="application/json")
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id"], 1)
            self.assertEqual(response.json[0]["name"], car.name)
            self.assertEqual(response.json[0]["platformHwId"], car.platform_hw_id)
            self.assertEqual(response.json[0]["underTest"], car.under_test)
            self.assertEqual(response.json[0]["defaultRouteId"], car.default_route_id)
            self.assertEqual(response.json[0]["carAdminPhone"]["phone"], car.car_admin_phone.phone)

    def test_creating_and_retrieving_two_cars(self):
        car_1 = Car(name="Test Car 1", platform_hw_id=1, car_admin_phone=PHONE)
        car_2 = Car(name="Test Car 2", platform_hw_id=2, car_admin_phone=PHONE)
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car_1], content_type="application/json")
            c.post("/v2/management/car", json=[car_2], content_type="application/json")
            response = c.get("/v2/management/car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_creating_car_from_invalid_data_returns_400_error_code(self):
        car_dict_missing_an_admin_phone = {"name": "Test Car", "platformId": 1}
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post(
                "/v2/management/car",
                json=car_dict_missing_an_admin_phone,
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)

    def test_creating_car_with_already_existing_name_returns_400_error_code(self):
        car_1 = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        car_2 = Car(name="Test Car", platform_hw_id=2, car_admin_phone=PHONE)
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car_1], content_type="application/json")
            response = c.post("/v2/management/car", json=[car_2], content_type="application/json")
            self.assertEqual(response.status_code, 400)

    def test_creating_car_using_invalid_json_returns_400_error_code(self):
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/car", json=7)
            self.assertEqual(response.status_code, 400)


class Test_Cars_With_Identical_Names(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")
        self.app = _app.get_test_app(
            "testAPIKey", accessible_tenants=["tenant_1", "tenant_2"], use_previous=True
        )
        with self.app.app.test_client() as client:
            client.set_cookie("", "tenant", "tenant_1")
            client.post(
                "/v2/management/platformhw?api_key=testAPIKey", json=[PlatformHW(name="test_hw_1")]
            )
            client.post(
                "/v2/management/platformhw?api_key=testAPIKey", json=[PlatformHW(name="test_hw_2")]
            )
            client.set_cookie("", "tenant", "tenant_2")
            client.post(
                "/v2/management/platformhw?api_key=testAPIKey", json=[PlatformHW(name="test_hw")]
            )

    def test_creating_two_cars_ith_identical_naems_under_the_same_tenant_returns_error(
        self,
    ) -> None:

        with self.app.app.test_client() as client:
            car_a = Car(name="Car", platform_hw_id=1, car_admin_phone=PHONE)
            car_b = Car(name="Car", platform_hw_id=2, car_admin_phone=PHONE)
            client.set_cookie("", "tenant", "tenant_1")
            client.post("/v2/management/car?api_key=testAPIKey", json=[car_a])
            response = client.post("/v2/management/car?api_key=testAPIKey", json=[car_b])
            self.assertEqual(response.status_code, 400)

    def test_creating_two_cars_with_identical_naems_under_different_tenants_is_allowed(
        self,
    ) -> None:

        with self.app.app.test_client() as client:
            car_a = Car(name="Car", platform_hw_id=1, car_admin_phone=PHONE)
            car_b = Car(name="Car", platform_hw_id=2, car_admin_phone=PHONE)
            client.set_cookie("", "tenant", "tenant_1")
            response_1 = client.post("/v2/management/car?api_key=testAPIKey", json=[car_a])
            client.set_cookie("", "tenant", "tenant_2")
            response_2 = client.post("/v2/management/car?api_key=testAPIKey", json=[car_b])
            self.assertEqual(response_2.status_code, 200)
            assert response_1.json is not None
            assert response_2.json is not None
            self.assertEqual(response_1.json[0]["name"], "Car")
            self.assertEqual(response_2.json[0]["name"], "Car")

    def test_car_access_across_tenant_boundaries_is_prevented(self):
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client() as client:
            # Create car in tenant_1
            client.set_cookie("", "tenant", "tenant_1")
            response = client.post("/v2/management/car?api_key=testAPIKey", json=[car])
            self.assertEqual(response.status_code, 200)
            car_id = response.json[0]["id"]

            # Attempt to access from tenant_2
            client.set_cookie("", "tenant", "tenant_2")
            response = client.get(f"/v2/management/car/{car_id}?api_key=testAPIKey")
            self.assertEqual(response.status_code, 404)

    def tearDown(self):
        clear_auth_params()
        clear_test_keys()


class Test_Retrieving_Single_Car(api_test.TestCase):
    def setUp(self, *args) -> None:
        super().setUp()
        platformhw = PlatformHW(name="Test Platform HW")
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/platformhw", json=[platformhw])

    def test_retrieving_single_existing_car(self):
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car], content_type="application/json")
            response = c.get("/v2/management/car/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], car.name)

    def test_retrieving_nonexistent_car_returns_code_404(self):
        nonexistent_car_id = 25
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car], content_type="application/json")
            response = c.get(f"/v2/management/car/{nonexistent_car_id}")
            self.assertEqual(response.status_code, 404)


class Test_Retrieving_Cars_Without_Valid_JWT_Token(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")
        self.app = _app.get_test_app("testAPIKey", accessible_tenants=[], use_previous=True)

    def test_token_without_any_tenants_yields_401_response(self):
        with self.app.app.test_client() as client:
            response = client.get(
                "/v2/management/platformhw", headers={"Authorization": f"Bearer {_app.get_token()}"}
            )
            self.assertEqual(response.status_code, 401)


class Test_Creating_Car_Using_Example_From_Specification(api_test.TestCase):
    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        create_stops(self.app, 3)
        create_route(self.app, stop_ids=(1, 2))

    def test_posting_and_getting_car_from_example_in_specification(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            example = c.get("/v2/management/openapi.json").json["components"]["schemas"]["Car"][
                "example"
            ]
            c.post("/v2/management/car", json=[example], content_type="application/json")
            response = c.get(f"/v2/management/car/{example['id']}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], example["name"])


class Test_Logging_Car_Creation(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, api_key=self.app.predef_api_key)

    def test_succesfull_creation_of_a_car_is_logged_as_info(self):
        with self.assertLogs(LOGGER_NAME, level="INFO") as logs:
            car = Car(name="test_car", platform_hw_id=1, car_admin_phone=PHONE)
            with self.app.app.test_client(TEST_TENANT_NAME) as c:
                c.set_cookie("", "tenant", TEST_TENANT_NAME)
                c.post("/v2/management/car", json=[car], content_type="application/json")
                # there should be three logs - one for a car, another for the car state and the last one for the car action state
                self.assertEqual(len(logs.output), 3)
                self.assertIn(str(car.name), logs.output[0])

    def test_unsuccesfull_creation_of_a_car_already_present_in_database_is_logged_as_s(
        self,
    ):
        with self.assertLogs(LOGGER_NAME, level="ERROR") as logs:
            car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
            app = _app.get_test_app(use_previous=True)
            with app.app.test_client(TEST_TENANT_NAME) as c:
                c.post("/v2/management/car", json=[car], content_type="application/json")
                c.post("/v2/management/car", json=[car], content_type="application/json")
                self.assertEqual(len(logs.output), 1)


class Test_Updating_Car(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        app = _app.get_test_app(use_previous=True)
        create_platform_hws(app)

    def test_add_and_succesfully_update_car(self) -> None:
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car], content_type="application/json")
            car.name = "Updated Test Car"
            car.id = 1
            response = c.put("/v2/management/car", json=[car], content_type="application/json")

            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/car")
            self.assertEqual(len(response.json), 1)  # type: ignore
            self.assertEqual(response.json[0]["name"], "Updated Test Car")  # type: ignore

    def test_updating_nonexistent_car_yields_404_error(self) -> None:
        car = Car(id=1, name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.put("/v2/management/car", json=[car], content_type="application/json")
            self.assertEqual(response.status_code, 404)

    def test_passing_other_object_when_updating_car_yields_400_error(self) -> None:
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        app = _app.get_test_app(use_previous=True)
        with app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            response = c.put("/v2/management/car", json={"id": 1}, content_type="application/json")
            self.assertEqual(response.status_code, 400)


class Test_Deleting_Car(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, tenant=TEST_TENANT_NAME)
        create_stops(self.app, 7)
        create_route(self.app, stop_ids=(2, 4, 6))

    def test_add_and_delete_car(self) -> None:
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            response = c.delete("/v2/management/car/1")
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/car")
            self.assertEqual(response.json, [])

    def test_deleting_nonexistent_car_yields_404_error(self) -> None:
        car_id = 17
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.delete(f"/v2/management/car/{car_id}")
            self.assertEqual(response.status_code, 404)

    def test_car_with_assigned_order_cannot_be_deleted(self):
        order = Order(
            id=1,
            is_visible=True,
            car_id=1,
            target_stop_id=2,
            stop_route_id=1,
        )
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/order", json=[order])
            response = c.delete("/v2/management/car/1")
            self.assertEqual(response.status_code, 400)


class Test_All_Cars_Must_Have_Unique_PlatformHWId(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)

    def test_creating_car_using_platformhw_assigned_to_other_car_yields_code_400(self):
        car_1 = Car(name="Test Car 1", platform_hw_id=1, car_admin_phone=PHONE)
        car_2 = Car(name="Test Car 2", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/car", json=[car_1], content_type="application/json")
            self.assertEqual(response.status_code, 200)
            response = c.post("/v2/management/car", json=[car_2], content_type="application/json")
            self.assertEqual(response.status_code, 400)


class Test_Retrieving_Car_With_States_Deleted(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        self.tenant = TenantFromTokenMock(current=TEST_TENANT_NAME)
        create_platform_hws(self.app)

    def test_car_state_is_none_for_car_whose_states_have_been_deleted(self):
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car], content_type="application/json")
            # delete only existing car state (using the database-access method delete instead of the API, which does not provide the delete method for car states)
            delete(self.tenant, CarStateDB, 1)
            response = c.get("/v2/management/carstate/1")
            # there are now no car states for car with ID=1
            self.assertEqual(response.json, [])
            # when getting car with ID=1, the default car state should be created
            response = c.get("/v2/management/car/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Car.from_dict(response.json).last_state, None)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(buffer=True)
