import sys
sys.path.append('.')
import unittest

from server.fleetman_http_api import Car
from server.fleetman_http_api.impl.controllers import get_cars, create_car


class Test_Cars(unittest.TestCase):

    def test_cars_list_is_initially_available_and_empty(self):
        cars, code = get_cars()
        self.assertEqual(code, 200)
        self.assertEqual(cars, [])

    def test_creating_a_car(self):
        car = Car(id=1, name="Test Car")
        create_car({"id": 1, "name": "Test Car"})


if __name__=="__main__":
    unittest.main()
