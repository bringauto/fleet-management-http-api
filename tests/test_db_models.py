import unittest

import fleet_management_api.api_impl.controllers as controllers
from fleet_management_api.models import Car


class Test_Creating_Car_DB_Model(unittest.TestCase):

    def test_creating_car_db_model_from_car_object(self):
        car = Car(id=1, name='test_car', platform_id=5)
        car_db_model = controllers.car_to_db_model(car)
        self.assertEqual(car_db_model.id, car.id)
        self.assertEqual(car_db_model.name, car.name)
        self.assertEqual(car_db_model.platform_id, car.platform_id)
        self.assertEqual(car_db_model.car_admin_phone, car.car_admin_phone)
        self.assertEqual(car_db_model.default_route_id, car.default_route_id)

    def test_car_converted_to_db_model_and_back_is_unchanged(self):
        car_in = Car(id=1, name='test_car', platform_id=5)
        car_out = controllers.car_from_db_model(controllers.car_to_db_model(car_in))
        self.assertEqual(car_out, car_in)


if __name__=="__main__":
    unittest.main()
