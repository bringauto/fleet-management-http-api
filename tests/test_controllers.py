import sys
sys.path.append('.')
import unittest

from fleet_management_api.models import Car
from fleet_management_api.app import get_app
from fleet_management_api.impl.controllers import get_cars, create_car


class Test_Cars(unittest.TestCase):

    def test_cars_list_is_initially_available_and_empty(self):
        app = get_app()
        with app.app.test_client() as c:
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_creating_a_car(self):
        car = Car(id=1, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            response = c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode().strip(), '"Car was succesfully created."')




if __name__=="__main__":
    unittest.main()
