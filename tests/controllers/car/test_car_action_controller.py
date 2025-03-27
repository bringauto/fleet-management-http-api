import unittest
from unittest.mock import patch, Mock
import time

import concurrent.futures as _futures

import fleet_management_api.app as _app
from fleet_management_api.models import (
    Car,
    CarActionStatus,
    CarActionState,
    MobilePhone,
)
from fleet_management_api.database.db_models import CarActionStateDB
from fleet_management_api.api_impl.controllers.car_action import (
    create_car_action_states_from_argument_and_save_to_db,
    check_for_invalid_car_action_state_transitions,
    get_last_action_states,
)
import fleet_management_api.database.connection as _connection
from fleet_management_api.database.timestamp import timestamp_ms
from fleet_management_api.api_impl.auth_controller import (
    get_test_public_key,
    set_auth_params,
    generate_test_keys,
)

from tests._utils.setup_utils import create_platform_hws
import tests._utils.api_test as api_test
from tests._utils.constants import TEST_TENANT_NAME
from tests._utils.setup_utils import TenantFromTokenMock


PHONE = MobilePhone(phone="123456789")


class Test_Creating_Car_Action_State(api_test.TestCase):

    def setUp(self, test_db_path=""):
        super().setUp(test_db_path)
        self.app = _app.get_test_app(use_previous=True)

    def test_for_nonexistent_car_yields_404_error(self):
        state = CarActionState(car_id=1, action_status=CarActionStatus.NORMAL)
        with self.app.app.test_client(TEST_TENANT_NAME):
            tenant = TenantFromTokenMock(current=TEST_TENANT_NAME)
            response = create_car_action_states_from_argument_and_save_to_db(tenant, [state])
            self.assertEqual(response.status_code, 404)

    def test_for_existing_car_yields_200_response(self):
        create_platform_hws(self.app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            state = CarActionState(car_id=1, action_status=CarActionStatus.PAUSED)
            response = create_car_action_states_from_argument_and_save_to_db(
                TenantFromTokenMock(current=TEST_TENANT_NAME), [state]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.body[0].action_status, CarActionStatus.PAUSED)


class Test_Adding_Action_State_Of_Existing_Car(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        self.car = Car(
            name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[self.car])

    def test_car_has_normal_action_state_by_default(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.get("/v2/management/action/car/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.NORMAL)

    def test_pausing_existing_car_with_normal_action_state_pauses_the_car(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            response = c.post("/v2/management/action/car/1/pause")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)

    def test_creating_action_state_for_existing_car_yields_200_response(self):
        state = CarActionState(car_id=1, action_status=CarActionStatus.PAUSED)
        tenant = TenantFromTokenMock(current=TEST_TENANT_NAME)
        response = create_car_action_states_from_argument_and_save_to_db(tenant, [state])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body[0].action_status, CarActionStatus.PAUSED)

    def test_after_pause_is_car_last_action_state_equal_to_paused(self):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/action/car/1/pause")
            response = c.get("/v2/management/action/car/1?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.PAUSED)


class Test_Merging_Action_States(api_test.TestCase):

    def test_empty_states_yield_empty_dict(self):
        states = []
        grouped_states = check_for_invalid_car_action_state_transitions(states)
        self.assertEqual(grouped_states, {})

    def test_no_consecutive_states_with_the_same_status_yield_unchanged_list(self):
        states = [
            CarActionState(car_id=1, action_status=CarActionStatus.NORMAL),
            CarActionState(car_id=1, action_status=CarActionStatus.PAUSED),
            CarActionState(car_id=7, action_status=CarActionStatus.NORMAL),
            CarActionState(car_id=4, action_status=CarActionStatus.PAUSED),
        ]
        invalid_transitions = check_for_invalid_car_action_state_transitions(states)
        self.assertDictEqual(invalid_transitions, dict())

    def test_consecutive_states_with_identical_status_are_merged(self):
        states = [
            CarActionState(car_id=1, action_status=CarActionStatus.NORMAL),
            CarActionState(car_id=1, action_status=CarActionStatus.PAUSED),
            CarActionState(car_id=1, action_status=CarActionStatus.PAUSED),
            CarActionState(car_id=2, action_status=CarActionStatus.PAUSED),
            CarActionState(car_id=2, action_status=CarActionStatus.NORMAL),
            CarActionState(car_id=3, action_status=CarActionStatus.PAUSED),
            CarActionState(car_id=2, action_status=CarActionStatus.NORMAL),
            CarActionState(car_id=3, action_status=CarActionStatus.NORMAL),
        ]
        invalid_transitions = check_for_invalid_car_action_state_transitions(states)
        self.assertDictEqual(
            invalid_transitions,
            {
                1: [(CarActionStatus.PAUSED, CarActionStatus.PAUSED)],
                2: [(CarActionStatus.NORMAL, CarActionStatus.NORMAL)],
            },
        )


class Test_Getting_Last_Action_States(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        self.car_1 = Car(
            name="Test Car 1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789")
        )
        self.car_2 = Car(
            name="Test Car 2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="123456789")
        )
        self.tenant = TenantFromTokenMock(current=TEST_TENANT_NAME)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[self.car_1, self.car_2])

    def test_getting_last_action_states_after_car_creation_yields_default_states(self):
        states = get_last_action_states(self.tenant, 1, 2)
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].action_status, CarActionStatus.NORMAL)
        self.assertEqual(states[1].action_status, CarActionStatus.NORMAL)

    def test_id_of_nonexistent_car_is_ignored_when_retrieving_last_states(self):
        states = get_last_action_states(self.tenant, 1, 4, 2, 3)
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].action_status, CarActionStatus.NORMAL)
        self.assertEqual(states[1].action_status, CarActionStatus.NORMAL)

    def test_last_action_states_contain_the_last_action_state_posted(self) -> None:
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/action/car/1/pause")
            states = get_last_action_states(self.tenant, 2, 1)
            self.assertEqual(len(states), 2)
            self.assertEqual(states[0].action_status, CarActionStatus.NORMAL)
            self.assertEqual(states[1].action_status, CarActionStatus.PAUSED)


class Test_Pausing_And_Unpausing_Car(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app)
        self.car = Car(
            name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789")
        )
        self.tenant = TenantFromTokenMock(current=TEST_TENANT_NAME)
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[self.car])
            response = c.get("/v2/management/action/car/1?lastN=1")
            assert response.json is not None
            self.last_timestamp = response.json[-1]["timestamp"]

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_pausing_car_in_normal_state_creates_new_state_with_paused_status(self, tmock: Mock):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            tmock.return_value = self.last_timestamp + 1000
            response = c.post("/v2/management/action/car/1/pause")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)
            self.assertEqual(response.json[0]["timestamp"], self.last_timestamp + 1000)

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_pausing_car_in_paused_state_does_not_create_new_action_state_and_yields_400_code(
        self, tmock: Mock
    ):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            tmock.return_value = self.last_timestamp + 1000
            c.post("/v2/management/action/car/1/pause")
            self.assertEqual(
                get_last_action_states(self.tenant, 1)[0].action_status, CarActionStatus.PAUSED
            )
            tmock.return_value += 2000
            response = c.post("/v2/management/action/car/1/pause")
            self.assertEqual(response.status_code, 400)
            response = c.get("/v2/management/action/car/1")
            assert response.json is not None
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.PAUSED)
            self.assertEqual(response.json[-1]["timestamp"], self.last_timestamp + 1000)

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_unpausing_car_in_paused_state_does_create_new_action_state_with_normal_status_any_yields_code_200(
        self, tmock: Mock
    ):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            tmock.return_value = self.last_timestamp + 1000
            c.post("/v2/management/action/car/1/pause")
            tmock.return_value = self.last_timestamp + 2000
            response = c.post("/v2/management/action/car/1/unpause")
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/action/car/1")
            assert response.json is not None
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.NORMAL)
            self.assertEqual(response.json[-1]["timestamp"], self.last_timestamp + 2000)

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_unpausing_unpaused_car_does_not_create_new_action_state_and_yields_code_400(
        self, tmock: Mock
    ):
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            tmock.return_value = self.last_timestamp + 1000
            c.post("/v2/management/action/car/1/pause")
            tmock.return_value = self.last_timestamp + 2000
            c.post("/v2/management/action/car/1/unpause")
            tmock.return_value = self.last_timestamp + 3000
            response = c.post("/v2/management/action/car/1/unpause")
            self.assertEqual(response.status_code, 400)
            response = c.get("/v2/management/action/car/1")
            assert response.json is not None
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.NORMAL)
            self.assertEqual(response.json[-1]["timestamp"], self.last_timestamp + 2000)


class Test_Query_Parameters(api_test.TestCase):

    def setUp(self, test_db_path=""):
        super().setUp(test_db_path)
        self.app = _app.get_test_app(use_previous=True)

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_only_states_inclusively_newer_than_since_parameter_value_are_returned(
        self, tmock: Mock
    ):
        create_platform_hws(self.app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            tmock.return_value = 1000
            c.post("/v2/management/car", json=[car])
            tmock.return_value = 2000
            c.post("/v2/management/action/car/1/pause")
            response = c.get("/v2/management/action/car/1?since=1500")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)

    def test_last_n_parameter_limits_number_of_returned_states(self):
        create_platform_hws(self.app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client(TEST_TENANT_NAME) as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/action/car/1/pause")
            c.post("/v2/management/action/car/1/unpause")
            response = c.get("/v2/management/action/car/1?lastN=1")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.NORMAL)

    def test_wait_parameter_yields_empty_response_when_no_new_states_are_posted(self):
        create_platform_hws(self.app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with _futures.ThreadPoolExecutor() as ex:
            with self.app.app.test_client(TEST_TENANT_NAME) as c:
                c.post("/v2/management/car", json=[car]).json
                time.sleep(1)
                timestamp = timestamp_ms()
                f1 = ex.submit(c.get, f"/v2/management/action/car/1?wait=true&since={timestamp}")
                time.sleep(1)
                c.post("/v2/management/action/car/1/pause")
                response = f1.result()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)


class Test_Maximum_Number_Of_States(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(
        self,
    ):
        max_n = CarActionStateDB.max_n_of_stored_states()
        with self.app.app.test_client() as c:
            c.post("/v2/management/action/car/1/pause")
            is_paused = True
            for _ in range(1, max_n - 2):
                op = "unpause" if is_paused else "pause"
                c.post(f"/v2/management/action/car/1/{op}")
                is_paused = not is_paused

            response = c.get("/v2/management/action/car/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n - 1)

            op = "unpause" if is_paused else "pause"
            c.post(f"/v2/management/action/car/1/{op}")
            is_paused = not is_paused

            response = c.get("/v2/management/action/car/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)

            op = "unpause" if is_paused else "pause"
            c.post(f"/v2/management/action/car/1/{op}")
            is_paused = not is_paused

            response = c.get("/v2/management/action/car/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)
            self.assertTrue(isinstance(response.json, list))

    def test_max_states_in_db_for_two_cars_is_double_of_max_n_of_states_for_single_car(self):
        car_2 = Car(name="car2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car_2])

        CarActionStateDB.set_max_n_of_stored_states(5)
        max_n = CarActionStateDB.max_n_of_stored_states()
        with self.app.app.test_client() as c:
            is_paused = False
            for _ in range(0, max_n + 5):
                op = "unpause" if is_paused else "pause"
                c.post(f"/v2/management/action/car/1/{op}")
                is_paused = not is_paused
            is_paused = False
            for _ in range(max_n, 2 * max_n + 5):
                op = "unpause" if is_paused else "pause"
                c.post(f"/v2/management/action/car/2/{op}")
                is_paused = not is_paused
            self.assertEqual(len(c.get("/v2/management/action/car/1?since=0").json), max_n)
            self.assertEqual(len(c.get("/v2/management/action/car/2?since=0").json), max_n)


class Test_List_Of_States_Is_Deleted_If_Car_Is_Deleted(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 1)
        car = Car(platform_hw_id=1, name="car1", car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_no_action_states_exists_for_car_after_car_is_deleted(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/action/car/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.NORMAL)

            c.delete("/v2/management/car/1")
            response = c.get("/v2/management/action/car/1")
            self.assertEqual(response.status_code, 404)


class Test_Returning_Last_N_Car_States(api_test.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mocked_timestamp: Mock) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 1)
        car = Car(platform_hw_id=1, name="car1", car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client() as c:
            mocked_timestamp.return_value = 0
            c.post("/v2/management/car", json=[car])

            mocked_timestamp.return_value = 1000
            c.post("/v2/management/action/car/1/pause")
            mocked_timestamp.return_value = 2000
            c.post("/v2/management/action/car/1/unpause")

    def test_returning_last_1_state(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/action/car/1?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.NORMAL)

    def test_returning_last_2_states(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/action/car/1?lastN=2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)
            self.assertEqual(response.json[1]["actionStatus"], CarActionStatus.NORMAL)

    def test_setting_last_n_to_higher_value_than_number_of_existing_states_yields_all_existing_states(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/action/car/1?lastN=100000")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.NORMAL)
            self.assertEqual(response.json[1]["actionStatus"], CarActionStatus.PAUSED)
            self.assertEqual(response.json[2]["actionStatus"], CarActionStatus.NORMAL)

    def test_returning_last_two_states_newer_than_given_timestamp(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/action/car/1?lastN=2&since=1500")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.NORMAL)


class Test_Returning_Last_N_Car_States_For_Given_Car(api_test.TestCase):

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def setUp(self, mocked_timestamp: Mock) -> None:
        super().setUp()
        self.app = _app.get_test_app(use_previous=True)
        create_platform_hws(self.app, 2)
        self.car_1 = Car(
            platform_hw_id=1, name="car1", car_admin_phone=MobilePhone(phone="123456789")
        )
        self.car_2 = Car(
            platform_hw_id=2, name="car2", car_admin_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client() as c:
            mocked_timestamp.return_value = 0
            response = c.post("/v2/management/car", json=[self.car_1, self.car_2])
            assert response.json is not None
            self.car_1.id = response.json[0]["id"]
            self.car_2.id = response.json[1]["id"]

        with self.app.app.test_client() as c:
            c.post("/v2/management/action/car/2/pause")
            mocked_timestamp.return_value = 1000
            c.post("/v2/management/action/car/1/pause")
            c.post("/v2/management/action/car/2/unpause")
            mocked_timestamp.return_value = 2000
            c.post("/v2/management/action/car/1/unpause")
            c.post("/v2/management/action/car/2/pause")

    def test_returning_last_1_state_for_given_car(self):
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/action/car/{self.car_1.id}?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.NORMAL)

        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/action/car/{self.car_2.id}?lastN=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)

    def test_returning_last_2_states_for_given_car(self):
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/action/car/{self.car_1.id}?lastN=2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)
            self.assertEqual(response.json[1]["actionStatus"], CarActionStatus.NORMAL)


class Test_Car_Action_States_Without_Tenant_In_Cookies(unittest.TestCase):

    def setUp(self, *args) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app(use_previous=True, predef_api_key="test_key")
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

    def test_pausing_car_is_allowed_without_cookie_set_if_car_owned_by_accessible_tenant(
        self,
    ) -> None:

        # car with id 1 is owned by tenant_A
        with self.app.app.test_client() as c:
            c.set_cookie("", "tenant", "")  # no tenant in cookies
            # post to car owned by tenant_A, that is accessible (present in the token)
            response = c.post(
                "/v2/management/action/car/1/pause",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
            )
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/action/car/1?api_key=test_key")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None, "No json in response"
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.PAUSED)

    def test_posting_car_state_to_tenant_is_not_allowed_if_car_is_owned_by_inaccessible_tenant(
        self,
    ) -> None:

        # car with id 1 is owned by tenant_A
        with self.app.app.test_client() as c:
            c.set_cookie("", "tenant", "")  # no tenant in cookies
            # post to car owned by tenant_C, that is inaccessible (missing from the token)
            response = c.post(
                "/v2/management/action/car/5/pause",
                headers={"Authorization": f"Bearer {_app.get_token('tenant_A', 'tenant_B')}"},
            )
            self.assertEqual(response.status_code, 401)
            response = c.get("/v2/management/action/car/5?api_key=test_key")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None, "No json in response"
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.NORMAL)


if __name__ == "__main__":  # pragma: no coverage
    unittest.main(buffer=True)
