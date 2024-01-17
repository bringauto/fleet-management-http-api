import unittest

from fleet_management_api.app import get_app
from fleet_management_api.models import Car, CarState, GNSSPosition
import fleet_management_api.database.connection as connection


class Test_Adding_New_Car_State(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_test_connection_source()

    def test_adding_new_car_state(self):
        car = Car(id=1, name="Test Car", platform_id=5)
        gnss_position = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=80, position=gnss_position)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json=car.to_dict())
            response = c.post('/v1/carstate', json=car_state.to_dict())
            self.assertEqual(response.status_code, 200)




if __name__ == '__main__':
    unittest.main() # pragma: no cover