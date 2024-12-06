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
from fleet_management_api.database.db_models import CarActionStateDBModel
from fleet_management_api.api_impl.controllers.car_action import (
    create_car_action_states_from_argument_and_save_to_db,
    check_for_invalid_car_action_state_transitions,
    get_last_action_states,
)
from fleet_management_api.database.timestamp import timestamp_ms

from tests._utils.setup_utils import create_platform_hws
import tests._utils.api_test as api_test


class Test_Creating_Car_Action_State(api_test.TestCase):

    def test_for_nonexistent_car_yields_404_error(self):
        state = CarActionState(car_id=1, action_status=CarActionStatus.NORMAL)
        response = create_car_action_states_from_argument_and_save_to_db([state])
        self.assertEqual(response.status_code, 404)

    def test_for_existing_car_yields_200_response(self):
        app = _app.get_test_app()
        create_platform_hws(app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])
            state = CarActionState(car_id=1, action_status=CarActionStatus.PAUSED)
            response = create_car_action_states_from_argument_and_save_to_db([state])
            print(response.body)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.body[0].action_status, CarActionStatus.PAUSED)


class Test_Adding_Action_State_Of_Existing_Car(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        self.car = Car(
            name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car])

    def test_car_has_normal_action_state_by_default(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/action/car/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[-1]["actionStatus"], CarActionStatus.NORMAL)

    def _test_pausing_existing_car_with_normal_action_state_pauses_the_car(self):
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/action/car/1/pause")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["actionStatus"], CarActionStatus.PAUSED)

    def test_creating_action_state_for_existing_car_yields_200_response(self):
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car])
            state = CarActionState(car_id=1, action_status=CarActionStatus.PAUSED)
            response = create_car_action_states_from_argument_and_save_to_db([state])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.body[0].action_status, CarActionStatus.PAUSED)

    def test_after_pause_is_car_last_action_state_equal_to_paused(self):
        with self.app.app.test_client() as c:
            c.post("/v2/management/action/car/1/pause")
            response = c.get("/v2/management/car/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json["lastActionState"]["actionStatus"], CarActionStatus.PAUSED
            )


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
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        self.car_1 = Car(
            name="Test Car 1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789")
        )
        self.car_2 = Car(
            name="Test Car 2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[self.car_1, self.car_2])

    def test_getting_last_action_states_after_car_creation_yields_default_states(self):
        states = get_last_action_states(1, 2)
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].action_status, CarActionStatus.NORMAL)
        self.assertEqual(states[1].action_status, CarActionStatus.NORMAL)

    def test_id_of_nonexistent_car_is_ignored_when_retrieving_last_states(self):
        states = get_last_action_states(1, 4, 2, 3)
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].action_status, CarActionStatus.NORMAL)
        self.assertEqual(states[1].action_status, CarActionStatus.NORMAL)

    def test_last_action_states_contain_the_last_action_state_posted(self) -> None:
        with self.app.app.test_client() as c:
            c.post("/v2/management/action/car/1/pause")
            states = get_last_action_states(2, 1)
            self.assertEqual(len(states), 2)
            self.assertEqual(states[0].action_status, CarActionStatus.NORMAL)
            self.assertEqual(states[1].action_status, CarActionStatus.PAUSED)


class Test_Pausing_And_Unpausing_Car(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app()
        create_platform_hws(self.app)
        self.car = Car(
            name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/car", json=[self.car])
            assert response.json is not None
            self.last_timestamp = response.json[0]["lastActionState"]["timestamp"]

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_pausing_car_in_normal_state_creates_new_state_with_paused_status(self, tmock: Mock):
        with self.app.app.test_client() as c:
            tmock.return_value = self.last_timestamp + 1000
            response = c.post("/v2/management/action/car/1/pause")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            print(response.json)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.PAUSED)
            self.assertEqual(response.json[0]["timestamp"], self.last_timestamp + 1000)

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_pausing_car_in_paused_state_does_not_create_new_action_state_and_yields_400_code(
        self, tmock: Mock
    ):
        with self.app.app.test_client() as c:
            tmock.return_value = self.last_timestamp + 1000
            c.post("/v2/management/action/car/1/pause")
            self.assertEqual(get_last_action_states(1)[0].action_status, CarActionStatus.PAUSED)
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
        with self.app.app.test_client() as c:
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
        with self.app.app.test_client() as c:
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

    @patch("fleet_management_api.database.timestamp.timestamp_ms")
    def test_only_states_inclusively_newer_than_since_parameter_value_are_returned(
        self, tmock: Mock
    ):
        app = _app.get_test_app()
        create_platform_hws(app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with app.app.test_client() as c:
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
        app = _app.get_test_app()
        create_platform_hws(app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])
            c.post("/v2/management/action/car/1/pause")
            c.post("/v2/management/action/car/1/unpause")
            response = c.get("/v2/management/action/car/1?lastN=1")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["actionStatus"], CarActionStatus.NORMAL)

    def test_wait_parameter_yields_empty_response_when_no_new_states_are_posted(self):
        app = _app.get_test_app()
        create_platform_hws(app)
        car = Car(name="Test Car", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with _futures.ThreadPoolExecutor() as ex:
            with app.app.test_client() as c:
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
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        car = Car(name="car1", platform_hw_id=1, car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(
        self,
    ):
        max_n = CarActionStateDBModel.max_n_of_stored_states()
        with self.app.app.test_client() as c:
            c.post("/v2/management/action/car/1/pause")
            is_paused = True
            for _ in range(1, max_n - 2):
                if is_paused:
                    response = c.post("/v2/management/action/car/1/unpause")
                else:
                    response = c.post("/v2/management/action/car/1/pause")
                is_paused = not is_paused

            response = c.get("/v2/management/action/car/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n - 1)

            if is_paused:
                c.post("/v2/management/action/car/1/unpause")
            else:
                c.post("/v2/management/action/car/1/pause")
            is_paused = not is_paused

            response = c.get("/v2/management/action/car/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)

            if is_paused:
                c.post("/v2/management/action/car/1/unpause")
            else:
                c.post("/v2/management/action/car/1/pause")
            is_paused = not is_paused

            response = c.get("/v2/management/action/car/1?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)
            self.assertTrue(isinstance(response.json, list))

    def test_max_states_in_db_for_two_cars_is_double_of_max_n_of_states_for_single_car(self):
        car_2 = Car(name="car2", platform_hw_id=2, car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car_2])

        CarActionStateDBModel.set_max_n_of_stored_states(5)
        max_n = CarActionStateDBModel.max_n_of_stored_states()
        with self.app.app.test_client() as c:
            is_paused = False
            for _ in range(0, max_n + 5):
                if is_paused:
                    c.post(f"/v2/management/action/car/1/unpause")
                else:
                    c.post("/v2/management/action/car/1/pause")
                is_paused = not is_paused
            is_paused = False
            for _ in range(max_n, 2 * max_n + 5):
                if is_paused:
                    c.post("/v2/management/action/car/2/unpause")
                else:
                    c.post("/v2/management/action/car/2/pause")
                is_paused = not is_paused
            self.assertEqual(len(c.get("/v2/management/action/car/1?since=0").json), max_n)
            self.assertEqual(len(c.get("/v2/management/action/car/2?since=0").json), max_n)


class Test_List_Of_States_Is_Deleted_If_Car_Is_Deleted(api_test.TestCase):

    def setUp(self, *args) -> None:
        super().setUp()
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 1)
        car = Car(platform_hw_id=1, name="car1", car_admin_phone=MobilePhone(phone="123456789"))
        with self.app.app.test_client() as c:
            c.post("/v2/management/car", json=[car])

    def test_no_action_states_exists_for_car_after_car_is_deleted(self):
        with self.app.app.test_client() as c:
            response = c.get("/v2/management/action/car/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["actionStatus"], "normal")

            c.delete("/v2/management/car/1")
            response = c.get("/v2/management/action/car/1")
            self.assertEqual(response.status_code, 404)


if __name__ == "__main__":  # pragma: no coverage
    unittest.main(buffer=True)
