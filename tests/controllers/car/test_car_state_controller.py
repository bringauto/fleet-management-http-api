import unittest
import os
import sys
sys.path.append(".")

import fleet_management_api.app as _app
from fleet_management_api.models import Car, CarState, GNSSPosition
import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_models as _db_models
from tests.utils.setup_utils import create_platform_hw_ids


class Test_Adding_State_Of_Existing_Car(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hw_ids(self.app, 5)
        self.car = Car(id=1, name="Test Car", platform_hw_id=5)
        with self.app.app.test_client() as c:
            c.post('/v2/management/car', json=self.car)

    def test_adding_state_to_existing_car(self):
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        with self.app.app.test_client() as c:
            response = c.post('/v2/management/carstate', json=car_state)
            self.assertEqual(response.status_code, 200)

    def test_car_state_is_automatically_rewritten_when_posting_to_api(self):
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        original_state_id = 1654615684531
        car_state = CarState(id=original_state_id, status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        with self.app.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state)
            state = c.get(f'/v2/management/carstate/{self.car.id}?allAvailable=true').json[0]
            self.assertNotEqual(state["id"], original_state_id)
            print(state["id"], original_state_id)

    def test_adding_state_to_nonexisting_car_returns_code_404(self):
        nonexistent_car_id = 121651516
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=nonexistent_car_id, speed=7, fuel=80, position=gnss_position)
        with self.app.app.test_client() as c:
            response = c.post('/v2/management/carstate', json=car_state)
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_state_returns_code_400(self):
        with self.app.app.test_client() as c:
            response = c.post('/v2/management/carstate', json={})
            self.assertEqual(response.status_code, 400)


class Test_Adding_State_Using_Example_From_Spec(unittest.TestCase):

    def test_adding_state_using_example_from_spec(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hw_ids(self.app, 5)
        self.car = Car(id=1, name="Test Car", platform_hw_id=5)
        with self.app.app.test_client() as c:
            c.post('/v2/management/car', json=self.car)
            example = c.get('/v2/management/openapi.json').json["components"]["schemas"]["CarState"]["example"]
            response = c.post('/v2/management/carstate', json=example)
            self.assertEqual(response.status_code, 200)


class Test_Getting_All_Car_States(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hw_ids(self.app, 5, 6)
        car_1 = Car(id=12, platform_hw_id=5, name="car1", car_admin_phone={}, default_route_id=1, under_test=False)
        car_2 = Car(id=14, platform_hw_id=6, name="car2", car_admin_phone={}, default_route_id=1, under_test=False)
        with self.app.app.test_client() as c:
            c.post('/v2/management/car', json=car_1)
            c.post('/v2/management/car', json=car_2)

    def test_getting_all_car_states_when_state_has_been_created_yields_empty_list(self):
        with self.app.app.test_client() as c:
            response = c.get('/v2/management/carstate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_all_car_states(self):
        car_state_1 = CarState(id=3, status="idle", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        car_state_2 = CarState(id=7, status="idle", car_id=14, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        with self.app.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Getting_Car_State_For_Given_Car(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hw_ids(self.app, 1, 23)
        car_1 = Car(id=12, platform_hw_id=1, name="car1", car_admin_phone={}, default_route_id=1, under_test=False)
        car_2 = Car(id=13, platform_hw_id=23, name="car2", car_admin_phone={}, default_route_id=1, under_test=False)
        with self.app.app.test_client() as c:
            c.post('/v2/management/car', json=car_1)
            c.post('/v2/management/car', json=car_2)

    def test_getting_car_state_for_existing_car_before_any_state_has_been_created_yields_empty_list(self):
        with self.app.app.test_client() as c:
            response = c.get('/v2/management/carstate/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_car_state_for_existing_car_after_state_has_been_created_yields_list_with_the_single_state(self):
        car_state_1 = CarState(id=3, status="idle", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        car_state_2 = CarState(id=7, status="charging", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        with self.app.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_getting_car_state_for_nonexisting_car_returns_code_404(self):
        with self.app.app.test_client() as c:
            response = c.get('/v2/management/carstate/4651684651')
            self.assertEqual(response.status_code, 404)

    def test_getting_last_car_state(self):
        car_state_1 = CarState(id=7, status="charging", car_id=12)
        car_state_2 = CarState(id=9, status="out_of_order", car_id=12)
        with self.app.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate/12?allAvailable=false')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["status"], "out_of_order")

    def test_getting_all_car_states(self):
        car_state_1 = CarState(id=4, status="charging", car_id=12)
        car_state_2 = CarState(id=6, status="out_of_order", car_id=12)
        with self.app.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate/12?allAvailable=true')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Maximum_Number_Of_States_Stored(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app()
        create_platform_hw_ids(self.app, 1)
        car = Car(id=12, name="car1", platform_hw_id=1, car_admin_phone={})
        with self.app.app.test_client() as c:
            c.post('/v2/management/car', json=car)

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(self):
        test_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        max_n = _db_models.CarStateDBModel.max_n_of_stored_states()
        with self.app.app.test_client() as c:
            oldest_state = CarState(id=0, status="idle", car_id=12, fuel=50, speed=7, position=test_position)
            c.post('/v2/management/carstate', json=oldest_state)
            for i in range(1, max_n - 1):
                car_state = CarState(id=i, status="stopped_by_phone", car_id=12, fuel=50, speed=7, position=test_position)
                c.post('/v2/management/carstate', json=car_state)

            response = c.get('/v2/management/carstate/12?allAvailable=true')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n-1)

            car_state = CarState(id=max_n, status="stopped_by_phone", car_id=12, fuel=50, speed=7, position=test_position)
            c.post('/v2/management/carstate', json=car_state)
            response = c.get('/v2/management/carstate/12?allAvailable=true')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)

            newest_state = CarState(id=max_n + 1, status="stopped_by_phone", car_id=12, fuel=50, speed=7, position=test_position)
            c.post('/v2/management/carstate', json=newest_state)
            response = c.get('/v2/management/carstate/12?allAvailable=true')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), max_n)
            self.assertTrue(isinstance(response.json, list))

            ids = [state["id"] for state in response.json]
            self.assertFalse(oldest_state.id in ids)
            self.assertTrue(newest_state.id in ids)

    def test_maximum_number_of_states_in_db_for_two_cars_is_double_of_max_n_of_states_for_single_car(self):
        test_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        create_platform_hw_ids(self.app, 7)
        car_2 = Car(id=13, name="car2", platform_hw_id=7, car_admin_phone={})
        with self.app.app.test_client() as c:
            c.post('/v2/management/car', json=car_2)
        _db_models.CarStateDBModel.set_max_n_of_stored_states(5)
        max_n = _db_models.CarStateDBModel.max_n_of_stored_states()
        with self.app.app.test_client() as c:
            for i in range(0, max_n + 5):
                car_state = CarState(id=i, status="stopped_by_phone", car_id=12, fuel=50, speed=7, position=test_position)
                c.post('/v2/management/carstate', json=car_state)
            for i in range(max_n, 2*max_n+5):
                car_state = CarState(id=i, status="stopped_by_phone", car_id=13, fuel=50, speed=7, position=test_position)
                c.post('/v2/management/carstate', json=car_state)
            self.assertEqual(len(c.get('/v2/management/carstate/12?allAvailable=True').json), max_n)
            self.assertEqual(len(c.get('/v2/management/carstate/13?allAvailable=True').json), max_n)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_List_Of_States_Is_Deleted_If_Car_Is_Deleted(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hw_ids(self.app, 1)
        car = Car(id=12, platform_hw_id=1, name="car1", car_admin_phone={}, default_route_id=1, under_test=False)
        with self.app.app.test_client() as c:
            c.post('/v2/management/car', json=car)

    def test_car_states_are_deleted_when_car_is_deleted(self):
        state_1 = CarState(id=3, status="idle", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        state_2 = CarState(id=7, status="charging", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))

        with self.app.app.test_client() as c:
            c.post('/v2/management/carstate', json=state_1)
            c.post('/v2/management/carstate', json=state_2)
            response = c.get('/v2/management/carstate?allAvailable=true')
            self.assertEqual(len(response.json), 2)
            response = c.get('/v2/management/carstate/12?allAvailable=true')
            self.assertEqual(len(response.json), 2, "Assert car states have been created.")
            c.delete('/v2/management/car/12')
            response = c.get('/v2/management/car/12')
            self.assertEqual(response.status_code, 404, "Assert car has been deleted.")
            response = c.get('/v2/management/carstate?allAvailable=true')
            self.assertEqual(len(response.json), 0, "Assert car states have been deleted.")
            response = c.get('/v2/management/carstate/12?allAvailable=true')
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__': # pragma: no coverage
    unittest.main(buffer=True)