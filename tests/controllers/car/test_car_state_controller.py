import unittest
from unittest.mock import patch, Mock

import fleet_management_api.app as _app
from fleet_management_api.models import Car, CarState, GNSSPosition, MobilePhone, Tenant
import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_models as _db_models
from fleet_management_api.api_impl.auth_controller import (
    get_test_public_key,
    set_auth_params,
    generate_test_keys,
)

from tests._utils.setup_utils import create_platform_hws
import tests._utils.api_test as api_test
from tests._utils.constants import TEST_TENANT_NAME


PHONE = MobilePhone(phone="123456789")


class Test_Adding_State_Of_Existing_Car(api_test.TestCase):

    def setUp(self, *args) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        self.car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[self.car])

    def test_adding_state_to_existing_car(self):
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/carstate", json=[car_state])
            self.assertEqual(response.status_code, 200)

    def test_adding_state_to_nonexisting_car_returns_code_404(self):
        nonexistent_car_id = 121651516
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(
            status="idle",
            car_id=nonexistent_car_id,
            speed=7,
            fuel=80,
            position=gnss_position,
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/carstate", json=[car_state])
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_state_returns_code_400(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/carstate", json={})
            self.assertEqual(response.status_code, 400)


class Test_Adding_State_Using_Example_From_Spec(unittest.TestCase):

    def test_adding_state_using_example_from_spec(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        self.car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[self.car])
            example = c.get("/v2/management/openapi.json").json["components"]["schemas"][
                "CarState"
            ]["example"]
            response = c.post("/v2/management/carstate", json=[example])
            self.assertEqual(response.status_code, 200)


class Test_Getting_All_Car_States(unittest.TestCase):

    def setUp(self, *args) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        car_1 = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        car_2 = Car(platform_hw_id=2, name="car2", car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car_1])
            c.post("/v2/management/car", json=[car_2])

    def test_getting_all_car_states(self):
        car_state_1 = CarState(
            status="idle",
            car_id=1,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )
        car_state_2 = CarState(
            status="idle",
            car_id=2,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/carstate", json=[car_state_1])
            c.post("/v2/management/carstate", json=[car_state_2])
            response = c.get("/v2/management/carstate")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 4)


class Test_Getting_Car_State_For_Given_Car(unittest.TestCase):

    def setUp(self, *args) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        car_1 = Car(
            platform_hw_id=1,
            name="car1",
            car_admin_phone=PHONE,
            under_test=False,
        )
        car_2 = Car(
            platform_hw_id=2,
            name="car2",
            car_admin_phone=PHONE,
            under_test=False,
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car_1])
            c.post("/v2/management/car", json=[car_2])

    def test_a_car_state_is_automatically_created_for_any_new_car(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_getting_car_state_for_existing_car_after_state_has_been_created_yields_list_with_the_single_state(
        self,
    ):
        car_state_1 = CarState(
            status="idle",
            car_id=1,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )
        car_state_2 = CarState(
            status="charging",
            car_id=1,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/carstate", json=[car_state_1])
            c.post("/v2/management/carstate", json=[car_state_2])
            response = c.get("/v2/management/carstate/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)

    def test_getting_car_state_for_nonexisting_car_returns_code_404(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate/4651684651")
            self.assertEqual(response.status_code, 404)

    def test_getting_last_car_state(self):
        car_state_1 = CarState(status="charging", car_id=1)
        car_state_2 = CarState(status="out_of_order", car_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/carstate", json=[car_state_1])
            c.post("/v2/management/carstate", json=[car_state_2])
            response = c.get("/v2/management/carstate/1?")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["status"], "out_of_order")

    def test_getting_all_car_states(self):
        car_state_1 = CarState(status="charging", car_id=1)
        car_state_2 = CarState(status="out_of_order", car_id=1)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/carstate", json=[car_state_1])
            c.post("/v2/management/carstate", json=[car_state_2])
            response = c.get("/v2/management/carstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)


class Test_Maximum_Number_Of_States_Stored(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(
        self,
    ):
        test_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        max_n = _db_models.CarStateDB.max_n_of_stored_states()
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            oldest_state = CarState(
                status="idle", car_id=1, fuel=50, speed=7, position=test_position
            )
            c.post("/v2/management/carstate", json=[oldest_state])
            for _ in range(1, max_n - 2):
                car_state = CarState(
                    status="paused_by_button",
                    car_id=1,
                    fuel=50,
                    speed=7,
                    position=test_position,
                )
                c.post("/v2/management/carstate", json=[car_state])

            response = c.get("/v2/management/carstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n - 1)

            car_state = CarState(
                status="paused_by_button",
                car_id=1,
                fuel=50,
                speed=7,
                position=test_position,
            )
            c.post("/v2/management/carstate", json=[car_state])
            response = c.get("/v2/management/carstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)

            newest_state = CarState(
                status="paused_by_button",
                car_id=1,
                fuel=50,
                speed=7,
                position=test_position,
            )
            c.post("/v2/management/carstate", json=[newest_state])
            response = c.get("/v2/management/carstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)
            self.assertTrue(isinstance(response.json, list))

    def test_maximum_number_of_states_in_db_for_two_cars_is_double_of_max_n_of_states_for_single_car(
        self,
    ):
        test_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_2 = Car(name="car2", platform_hw_id=2, car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car_2])
        _db_models.CarStateDB.set_max_n_of_stored_states(5)
        max_n = _db_models.CarStateDB.max_n_of_stored_states()
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            for i in range(0, max_n + 5):
                car_state = CarState(
                    status="paused_by_button",
                    car_id=1,
                    fuel=50,
                    speed=7,
                    position=test_position,
                )
                c.post("/v2/management/carstate", json=[car_state])
            for i in range(max_n, 2 * max_n + 5):
                car_state = CarState(
                    status="paused_by_button",
                    car_id=2,
                    fuel=50,
                    speed=7,
                    position=test_position,
                )
                c.post("/v2/management/carstate", json=[car_state])
            self.assertEqual(len(c.get("/v2/management/carstate/1?since=0").json), max_n)
            self.assertEqual(len(c.get("/v2/management/carstate/2?since=0").json), max_n)


class Test_List_Of_States_Is_Deleted_If_Car_Is_Deleted(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 1)
        car = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/car", json=[car])
            assert response.json is not None

    def test_car_states_are_deleted_when_car_is_deleted(self):
        state_1 = CarState(
            status="idle",
            car_id=1,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )
        state_2 = CarState(
            status="charging",
            car_id=1,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/carstate", json=[state_1])
            c.post("/v2/management/carstate", json=[state_2])
            response = c.get("/v2/management/carstate?since=0")
            self.assertEqual(len(response.json), 3)
            response = c.get("/v2/management/carstate/1?since=0")
            self.assertEqual(len(response.json), 3, "Assert car states have been created.")
            c.delete("/v2/management/car/1")
            response = c.get("/v2/management/car/1")
            self.assertEqual(response.status_code, 404, "Assert car has been deleted.")
            response = c.get("/v2/management/carstate?since=0")
            self.assertEqual(len(response.json), 0, "Assert car states have been deleted.")
            response = c.get("/v2/management/carstate/1")
            self.assertEqual(response.status_code, 404)


class Test_Filtering_Car_States_By_Timestamp(api_test.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mocked_timestamp: Mock, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 1)
        car = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 0
            response = c.post("/v2/management/car", json=[car])
            assert response.json is not None
            car_id = response.json[0]["id"]

        state_1 = CarState(
            status="idle",
            car_id=car_id,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )
        state_2 = CarState(
            status="charging",
            car_id=car_id,
            speed=7,
            fuel=80,
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 1000
            c.post("/v2/management/carstate", json=[state_1])
            mocked_timestamp.return_value = 2000
            c.post("/v2/management/carstate", json=[state_2])

    def test_setting_since_to_zero_returns_all_states_of_given_car(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)

    def test_setting_since_to_1000_returns_states_created_after_timestamp_1000(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate/1?since=1000")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["timestamp"], 1000)

    def test_setting_since_to_3000_returns_empty_list(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate/1?since=3000")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)


POSITION = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)


class Test_Returning_Last_N_Car_States(api_test.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mocked_timestamp: Mock) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        car = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 0
            response = c.post("/v2/management/car", json=[car])
            assert response.json is not None
            car_id = response.json[0]["id"]

        state_1 = CarState(status="idle", car_id=car_id, position=POSITION)
        state_2 = CarState(status="charging", car_id=car_id, position=POSITION)

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 1000
            c.post("/v2/management/carstate", json=[state_1])
            mocked_timestamp.return_value = 2000
            c.post("/v2/management/carstate", json=[state_2])

    def test_returning_last_1_state(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "charging")

    def test_returning_last_2_states(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate?lastN=2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            print(response.json)
            self.assertEqual(response.json[0]["status"], "idle")
            self.assertEqual(response.json[1]["status"], "charging")

    def test_setting_last_n_to_higher_value_than_number_of_existing_states_yields_all_existing_states(
        self,
    ):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate?lastN=100000")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["status"], "out_of_order")
            self.assertEqual(response.json[1]["status"], "idle")
            self.assertEqual(response.json[2]["status"], "charging")

    def test_returning_last_two_states_newer_than_given_timestamp(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/carstate?lastN=2&since=1500")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "charging")

    def test_returning_last_timestamp_with_identical_timestamps_returns_the_one_with_higher_id(
        self,
    ):
        state_3 = CarState(status="out_of_order", car_id=1, position=POSITION)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/carstate", json=[state_3])
            response = c.get("/v2/management/carstate?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "out_of_order")


class Test_Returning_Last_N_Car_States_For_Given_Car(unittest.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mocked_timestamp: Mock) -> None:
        super().setUp()
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        self.car_1 = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        self.car_2 = Car(platform_hw_id=2, name="car2", car_admin_phone=PHONE)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 0
            response = c.post("/v2/management/car", json=[self.car_1, self.car_2])
            assert response.json is not None
            self.car_1 = Car.from_dict(response.json[0])
            self.car_2 = Car.from_dict(response.json[1])

        state_1 = CarState(status="idle", car_id=self.car_1.id, position=POSITION)
        state_2 = CarState(status="charging", car_id=self.car_1.id, position=POSITION)
        state_3 = CarState(status="idle", car_id=self.car_2.id, position=POSITION)
        state_4 = CarState(status="driving", car_id=self.car_2.id, position=POSITION)

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            mocked_timestamp.return_value = 1000
            c.post("/v2/management/carstate", json=[state_1, state_3])
            mocked_timestamp.return_value = 2000
            c.post("/v2/management/carstate", json=[state_2, state_4])

    def test_returning_last_1_state_for_given_car(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get(f"/v2/management/carstate/{self.car_1.id}?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "charging")

        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get(f"/v2/management/carstate/{self.car_2.id}?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "driving")

    def test_returning_last_2_states_for_given_car(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get(f"/v2/management/carstate/{self.car_1.id}?lastN=2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["status"], "idle")
            self.assertEqual(response.json[1]["status"], "charging")


class Test_Car_States_Without_Tenant_In_Cookies(unittest.TestCase):

    def setUp(self, *args) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True, predef_api_key="test_key")
        with self.app.app.test_client() as c:
            c.post(
                "/v2/management/tenant?api_key=test_key",
                json=[Tenant(name="tenant_A"), Tenant(name="tenant_B"), Tenant(name="tenant_C")],
            )
        create_platform_hws(self.app, 2, tenant="tenant_A", api_key="test_key")
        create_platform_hws(self.app, 2, tenant="tenant_B", api_key="test_key")
        create_platform_hws(self.app, 2, tenant="tenant_C", api_key="test_key")

        car_1 = Car(platform_hw_id=1, name="car1", car_admin_phone=PHONE)
        car_2 = Car(platform_hw_id=2, name="car2", car_admin_phone=PHONE)
        car_3 = Car(platform_hw_id=3, name="car3", car_admin_phone=PHONE)
        car_4 = Car(platform_hw_id=4, name="car4", car_admin_phone=PHONE)
        car_5 = Car(platform_hw_id=5, name="car5", car_admin_phone=PHONE)
        car_6 = Car(platform_hw_id=6, name="car6", car_admin_phone=PHONE)

        with self.app.app.test_client("tenant_A") as c:
            c.set_cookie("", "tenant", "tenant_A")
            response = c.post("/v2/management/car?api_key=test_key", json=[car_1, car_2])
            assert response.status_code == 200, response.json
        with self.app.app.test_client("tenant_B") as c:
            c.set_cookie("", "tenant", "tenant_B")
            response = c.post("/v2/management/car?api_key=test_key", json=[car_3, car_4])
            assert response.status_code == 200, response.json
        with self.app.app.test_client("tenant_C") as c:
            c.set_cookie("", "tenant", "tenant_C")
            response = c.post("/v2/management/car?api_key=test_key", json=[car_5, car_6])
            assert response.status_code == 200, response.json
        generate_test_keys()
        set_auth_params(get_test_public_key(strip=True), "test_client")

    def test_accessing_all_car_states_without_specifying_tenant_yields_states_of_cars_owned_by_accessible_tenants(
        self,
    ) -> None:
        with self.app.app.test_client() as c:
            response = c.get(
                "/v2/management/carstate",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
            )
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 4)
            for state in response.json:
                self.assertEqual(state["status"], "out_of_order")

    def test_posting_car_state_is_allowed_without_cookie_set_if_car_is_owned_by_accessible_tenant(
        self,
    ):
        # car with id 1 is owned by tenant_A
        state = CarState(status="idle", car_id=1)
        with self.app.app.test_client() as c:
            c.set_cookie("", "tenant", "")
            # post to car owned by tenant_A, that is accessible (present in the token)
            response = c.post(
                "/v2/management/carstate?api_key=test_key",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
                json=[state],
            )
            self.assertEqual(response.status_code, 200)
            assert response.json is not None, response.json
            self.assertEqual(response.json[0]["status"], "idle")
            self.assertEqual(response.json[0]["carId"], 1)

    def test_posting_car_state_is_not_allowed_if_car_is_owned_by_inaccessible_tenant(self):
        # car with id 5 is owned by tenant_C
        state = CarState(status="idle", car_id=5)
        with self.app.app.test_client() as c:
            c.set_cookie("", "tenant", "")
            # post to car owned by tenant_C, that is inaccessible (missing from the token)
            response = c.post(
                "/v2/management/carstate",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
                json=[state],
            )
            self.assertEqual(response.status_code, 401)


if __name__ == "__main__":  # pragma: no coverage
    unittest.main(buffer=True)
