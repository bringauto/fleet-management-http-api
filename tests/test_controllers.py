import sys
sys.path.append('.')
import unittest

from fleet_management_api.models import Car
from fleet_management_api.app import get_app


class Test_Cars(unittest.TestCase):

    def test_cars_list_is_initially_available_and_empty(self):
        app = get_app()
        with app.app.test_client() as c:
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_creating_and_retrieving_a_car(self):
        car = Car(id=1, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            response = c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, "Car was succesfully created.")
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_creating_and_retrieving_two_cars(self):
        car_1 = Car(id=1, name="Test Car 1", platform_id=5)
        car_2 = Car(id=2, name="Test Car 2", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car_1.to_dict(), content_type='application/json')
            c.post('/v1/car', json = car_2.to_dict(), content_type='application/json')
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


if __name__=="__main__":
    unittest.main()
