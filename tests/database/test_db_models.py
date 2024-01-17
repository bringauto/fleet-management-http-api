import unittest

import fleet_management_api.api_impl.obj_to_db as obj_to_db
from fleet_management_api.models import Car, MobilePhone


class Test_Creating_Car_DB_Model(unittest.TestCase):

    def test_creating_car_db_model_from_car_object_preserves_attribute_values(self):
        car = Car(
            id=1,
            name='test_car',
            platform_id=5,
            car_admin_phone=MobilePhone(phone='1234567890'),
            default_route_id=1
        )
        car_db_model = obj_to_db.car_to_db_model(car)
        self.assertEqual(car_db_model.id, car.id)
        self.assertEqual(car_db_model.name, car.name)
        self.assertEqual(car_db_model.platform_id, car.platform_id)
        self.assertEqual(car_db_model.default_route_id, car.default_route_id)
        phone_in_db_model = MobilePhone.from_dict(car_db_model.car_admin_phone)
        self.assertEqual(phone_in_db_model, car.car_admin_phone)

    def test_creating_car_db_model_from_car_object_with_only_required_attributes_specified_preserves_attribute_values(self):
        car = Car(id=1, name='test_car', platform_id=5)
        car_db_model = obj_to_db.car_to_db_model(car)
        self.assertEqual(car_db_model.id, car.id)
        self.assertEqual(car_db_model.name, car.name)
        self.assertEqual(car_db_model.platform_id, car.platform_id)
        self.assertEqual(car_db_model.car_admin_phone, car.car_admin_phone)
        self.assertEqual(car_db_model.default_route_id, car.default_route_id)

    def test_car_converted_to_db_model_and_back_is_unchanged(self):
        car_in = Car(id=1, name='test_car', platform_id=5)
        car_out = obj_to_db.car_from_db_model(obj_to_db.car_to_db_model(car_in))
        self.assertEqual(car_out, car_in)

    def test_car_with_all_attributes_specified_converted_to_db_model_and_back_is_unchanged(self):
        car_in = Car(id=1, name='test_car', platform_id=5, car_admin_phone=MobilePhone(phone='1234567890'), default_route_id=1)
        car_out = obj_to_db.car_from_db_model(obj_to_db.car_to_db_model(car_in))
        self.assertEqual(car_out, car_in)


if __name__=="__main__":
    unittest.main() # pragma: no cover
