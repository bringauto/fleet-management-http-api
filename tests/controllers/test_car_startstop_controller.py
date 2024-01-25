import unittest

import fleet_management_api.database.connection as _connection
from fleet_management_api.app import get_app
from fleet_management_api.models import Car


class Test_Car_StartStop_Controller(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_test_connection_source()

    def test_starting_or_stopping_existing_car_returns_code_200(self):
        car_id = 123
        car = Car(id=car_id, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json=car, content_type='application/json')
            response = c.get(f'/v1/car/startstop/{car_id}')
            self.assertEqual(response.status_code, 200)

    def test_starting_or_stopping_nonexistent_car_returns_code_404(self):
        car_id = 123
        app = get_app()
        with app.app.test_client() as c:
            response = c.get(f'/v1/car/startstop/{car_id}')
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main() # pragma: no cover