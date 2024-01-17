import unittest

import fleet_management_api.api_impl.db_models as db_models
from fleet_management_api.models import (
    Car,
    MobilePhone,
    CarState,
    GNSSPosition,
    Order,
    Priority,
    OrderStatus
)


class Test_Creating_Car_DB_Model(unittest.TestCase):

    def test_creating_car_db_model_from_car_object_preserves_attribute_values(self):
        car = Car(
            id=1,
            name='test_car',
            platform_id=5,
            car_admin_phone=MobilePhone(phone='1234567890'),
            default_route_id=1
        )
        car_db_model = db_models.car_to_db_model(car)
        self.assertEqual(car_db_model.id, car.id)
        self.assertEqual(car_db_model.name, car.name)
        self.assertEqual(car_db_model.platform_id, car.platform_id)
        self.assertEqual(car_db_model.default_route_id, car.default_route_id)
        phone_in_db_model = MobilePhone.from_dict(car_db_model.car_admin_phone)
        self.assertEqual(phone_in_db_model, car.car_admin_phone)

    def test_creating_car_db_model_from_car_object_with_only_required_attributes_specified_preserves_attribute_values(self):
        car = Car(id=1, name='test_car', platform_id=5)
        car_db_model = db_models.car_to_db_model(car)
        self.assertEqual(car_db_model.id, car.id)
        self.assertEqual(car_db_model.name, car.name)
        self.assertEqual(car_db_model.platform_id, car.platform_id)
        self.assertEqual(car_db_model.car_admin_phone, car.car_admin_phone)
        self.assertEqual(car_db_model.default_route_id, car.default_route_id)

    def test_car_converted_to_db_model_and_back_is_unchanged(self):
        car_in = Car(id=1, name='test_car', platform_id=5)
        car_out = db_models.car_from_db_model(db_models.car_to_db_model(car_in))
        self.assertEqual(car_out, car_in)

    def test_car_with_all_attributes_specified_converted_to_db_model_and_back_is_unchanged(self):
        car_in = Car(id=1, name='test_car', platform_id=5, car_admin_phone=MobilePhone(phone='1234567890'), default_route_id=1)
        car_out = db_models.car_from_db_model(db_models.car_to_db_model(car_in))
        self.assertEqual(car_out, car_in)


class Test_Creating_Car_State_DB_Model(unittest.TestCase):

    def test_creating_car_state_db_model_from_car_state_object_preserves_attribute_values(self):
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=8, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        car_state_db_model = db_models.car_state_to_db_model(car_state)
        self.assertEqual(car_state_db_model.id, car_state.id)
        self.assertEqual(car_state_db_model.status, car_state.status)
        self.assertEqual(car_state_db_model.car_id, car_state.car_id)
        self.assertEqual(car_state_db_model.speed, car_state.speed)
        self.assertEqual(car_state_db_model.fuel, car_state.fuel)
        self.assertEqual(car_state_db_model.position, car_state.position.to_dict())

    def test_creating_car_state_db_model_from_car_state_object_with_only_required_attributes_specified_preserves_attribute_values(self):
        car_state = CarState(id=12, status="idle", car_id=1)
        car_state_db_model = db_models.car_state_to_db_model(car_state)
        self.assertEqual(car_state_db_model.id, car_state.id)
        self.assertEqual(car_state_db_model.status, car_state.status)
        self.assertEqual(car_state_db_model.car_id, car_state.car_id)
        self.assertEqual(car_state_db_model.speed, car_state.speed)
        self.assertEqual(car_state_db_model.fuel, car_state.fuel)
        self.assertEqual(car_state_db_model.position, car_state.position)

    def test_car_state_converted_to_db_model_and_back_is_unchanged(self):
        state_in = CarState(id=12, status="idle", car_id=1)
        state_out = db_models.car_state_from_db_model(db_models.car_state_to_db_model(state_in))
        self.assertEqual(state_out, state_in)

    def test_car_state_with_all_attributes_specified_converted_to_db_model_and_back_is_unchanged(self):
        state_in = CarState(id=12, status="idle", car_id=1, speed=7, fuel=8, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        state_out = db_models.car_state_from_db_model(db_models.car_state_to_db_model(state_in))
        self.assertEqual(state_out, state_in)


class Test_Creating_Order_DB_Model(unittest.TestCase):

    def test_creating_db_model_from_order_preserves_attribute_values(self):
        order = Order(id=1, user_id=789, car_id=12, target_stop_id=7, stop_route_id=8)
        order_db_model = db_models.order_to_db_model(order)
        self.assertEqual(order_db_model.id, order.id)
        self.assertEqual(order_db_model.priority, order.priority)
        self.assertEqual(order_db_model.user_id, order.user_id)
        self.assertEqual(order_db_model.status, order.status)
        self.assertEqual(order_db_model.car_id, order.car_id)
        self.assertEqual(order_db_model.target_stop_id, order.target_stop_id)
        self.assertEqual(order_db_model.stop_route_id, order.stop_route_id)
        self.assertEqual(order_db_model.notification_phone, order.notification_phone)

    def test_creating_db_model_from_order_with_only_required_attributes_specified_preserves_attribute_values(self):
        order = Order(
            id=1,
            priority=Priority.NORMAL,
            user_id=789,
            car_id=12,
            status=OrderStatus.IN_PROGRESS,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        order_db_model = db_models.order_to_db_model(order)
        self.assertEqual(order_db_model.id, order.id)
        self.assertEqual(order_db_model.priority, order.priority)
        self.assertEqual(order_db_model.user_id, order.user_id)
        self.assertEqual(order_db_model.status, order.status)
        self.assertEqual(order_db_model.car_id, order.car_id)
        self.assertEqual(order_db_model.target_stop_id, order.target_stop_id)
        self.assertEqual(order_db_model.stop_route_id, order.stop_route_id)
        self.assertEqual(order_db_model.notification_phone, order.notification_phone.to_dict())

    def test_order_converted_to_db_model_and_back_is_unchanged(self):
        order_in = Order(id=1, user_id=789, car_id=12, target_stop_id=7, stop_route_id=8)
        order_out = db_models.order_from_db_model(db_models.order_to_db_model(order_in))
        self.assertEqual(order_out, order_in)

    def test_order_with_all_attributes_specified_converted_to_db_model_and_back_is_unchanged(self):
        order_in = Order(
            id=1,
            priority=Priority.HIGH,
            user_id=789,
            car_id=12,
            status=OrderStatus.IN_PROGRESS,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        order_out = db_models.order_from_db_model(db_models.order_to_db_model(order_in))
        self.assertEqual(order_out, order_in)



if __name__=="__main__":
    unittest.main() # pragma: no cover
