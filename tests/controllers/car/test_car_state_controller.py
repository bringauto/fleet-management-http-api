import unittest
import os

import fleet_management_api.app as _app
from fleet_management_api.models import Car, CarState, GNSSPosition
import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_models as _db_models


class Test_Adding_State_Of_Existing_Car(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.car = Car(id=1, name="Test Car", platform_id=5)
        self.app = _app.get_test_app().app
        with self.app.test_client() as c:
            c.post('/v2/management/car', json=self.car)

    def test_adding_state_to_existing_car(self):
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        with self.app.test_client() as c:
            response = c.post('/v2/management/carstate', json=car_state)
            self.assertEqual(response.status_code, 200)

    def test_adding_state_to_nonexisting_car_returns_code_404(self):
        nonexistent_car_id = 121651516
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=nonexistent_car_id, speed=7, fuel=80, position=gnss_position)
        with self.app.test_client() as c:
            response = c.post('/v2/management/carstate', json=car_state)
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_state_returns_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v2/management/carstate', json={})
            self.assertEqual(response.status_code, 400)

    def test_sending_repeatedly_status_with_identical_id_returns_code_400(self):
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        with self.app.test_client() as c:
            response = c.post('/v2/management/carstate', json=car_state)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v2/management/carstate', json=car_state)
            self.assertEqual(response.status_code, 400)


class Test_Adding_State_Using_Example_From_Spec(unittest.TestCase):

    def test_adding_state_using_example_from_spec(self):
        _connection.set_connection_source_test()
        self.car = Car(id=1, name="Test Car", platform_id=5)
        self.app = _app.get_test_app().app
        with self.app.test_client() as c:
            c.post('/v2/management/car', json=self.car)
            example = c.get('/v2/management/openapi.json').json["components"]["schemas"]["CarState"]["example"]
            response = c.post('/v2/management/carstate', json=example)
            self.assertEqual(response.status_code, 200)


class Test_Getting_All_Car_States(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        car_1 = Car(id=12, platform_id=1, name="car1", car_admin_phone={}, default_route_id=1, under_test=False)
        car_2 = Car(id=14, platform_id=1, name="car2", car_admin_phone={}, default_route_id=1, under_test=False)
        with self.app.test_client() as c:
            c.post('/v2/management/car', json=car_1)
            c.post('/v2/management/car', json=car_2)

    def test_getting_all_car_states_when_state_has_been_created_yields_empty_list(self):
        with self.app.test_client() as c:
            response = c.get('/v2/management/carstate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_all_car_states(self):
        car_state_1 = CarState(id=3, status="idle", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        car_state_2 = CarState(id=7, status="idle", car_id=14, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        with self.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Getting_Car_State_For_Given_Car(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        car_1 = Car(id=12, platform_id=1, name="car1", car_admin_phone={}, default_route_id=1, under_test=False)
        car_2 = Car(id=13, platform_id=78, name="car2", car_admin_phone={}, default_route_id=1, under_test=False)
        with self.app.test_client() as c:
            c.post('/v2/management/car', json=car_1)
            c.post('/v2/management/car', json=car_2)

    def test_getting_car_state_for_existing_car_before_any_state_has_been_created_yields_empty_list(self):
        with self.app.test_client() as c:
            response = c.get('/v2/management/carstate/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_getting_car_state_for_existing_car_after_state_has_been_created_yields_list_with_state(self):
        car_state_1 = CarState(id=3, status="idle", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        car_state_2 = CarState(id=7, status="charging", car_id=12, speed=7, fuel=80, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        with self.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id"], 7)

    def test_getting_car_state_for_nonexisting_car_returns_code_404(self):
        with self.app.test_client() as c:
            response = c.get('/v2/management/carstate/4651684651')
            self.assertEqual(response.status_code, 404)

    def test_getting_last_car_state(self):
        car_state_1 = CarState(id=7, status="charging", car_id=12)
        car_state_2 = CarState(id=9, status="out_of_order", car_id=12)
        with self.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate/12?allAvailable=false')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id"], 9)

    def test_getting_all_car_states(self):
        car_state_1 = CarState(id=4, status="charging", car_id=12)
        car_state_2 = CarState(id=6, status="out_of_order", car_id=12)
        with self.app.test_client() as c:
            c.post('/v2/management/carstate', json=car_state_1)
            c.post('/v2/management/carstate', json=car_state_2)
            response = c.get('/v2/management/carstate/12?allAvailable=true')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["id"], 4)
            self.assertEqual(response.json[1]["id"], 6)


class Test_Maximum_Number_Of_States_Stored(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test("test_db.db")
        self.app = _app.get_test_app().app
        car = Car(id=12, name="car1", platform_id=1, car_admin_phone={})
        with self.app.test_client() as c:
            c.post('/v2/management/car', json=car)

    def test_oldest_state_is_removed_when_max_n_plus_one_states_were_sent_to_database(self):
        test_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        max_n = _db_models.CarStateDBModel.max_n_of_stored_states()
        with self.app.test_client() as c:
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
        car_2 = Car(id=13, name="car2", platform_id=7, car_admin_phone={})
        with self.app.test_client() as c:
            c.post('/v2/management/car', json=car_2)

        _db_models.CarStateDBModel.set_max_n_of_stored_states(5)
        max_n = _db_models.CarStateDBModel.max_n_of_stored_states()
        with self.app.test_client() as c:
            for i in range(0, max_n + 5):
                car_state = CarState(id=i, status="stopped_by_phone", car_id=12, fuel=50, speed=7, position=test_position)
                c.post('/v2/management/carstate', json=car_state)

            for i in range(max_n, 2*max_n + 5):
                car_state = CarState(id=i, status="stopped_by_phone", car_id=13, fuel=50, speed=7, position=test_position)
                c.post('/v2/management/carstate', json=car_state)

            response = c.get('/v2/management/carstate')
            self.assertEqual(len(response.json), 2*max_n)



    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == '__main__': # pragma: no coverage
    unittest.main(buffer=True)