import unittest

from fleet_management_api.app import get_app
from fleet_management_api.models import Car, CarState, GNSSPosition
import fleet_management_api.database.connection as connection


class Test_Adding_State_Of_Existing_Car(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()
        self.car = Car(id=1, name="Test Car", platform_id=5)
        self.app = get_app().app
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car)

    def test_adding_state_to_existing_car(self):
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        with self.app.test_client() as c:
            response = c.post('/v1/carstate', json=car_state)
            self.assertEqual(response.status_code, 200)

    def test_adding_state_to_nonexisting_car_returns_code_404(self):
        nonexistent_car_id = 121651516
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=nonexistent_car_id, speed=7, fuel=80, position=gnss_position)
        with self.app.test_client() as c:
            response = c.post('/v1/carstate', json=car_state)
            self.assertEqual(response.status_code, 404)

    def test_sending_incomplete_state_returns_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/carstate', json={})
            self.assertEqual(response.status_code, 400)

    def test_sending_repeatedly_status_with_identical_id_returns_code_400(self):
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        with self.app.test_client() as c:
            response = c.post('/v1/carstate', json=car_state)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/carstate', json=car_state)
            self.assertEqual(response.status_code, 400)


class Test_Adding_State_Using_Example_From_Spec(unittest.TestCase):

    def test_adding_state_using_example_from_spec(self):
        connection.set_test_connection_source()
        self.car = Car(id=1, name="Test Car", platform_id=5)
        self.app = get_app().app
        with self.app.test_client() as c:
            c.post('/v1/car', json=self.car)
            example = c.get('/v1/openapi.json').json["components"]["schemas"]["CarState"]["example"]
            response = c.post('/v1/carstate', json=example)
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main() # pragma: no coverage