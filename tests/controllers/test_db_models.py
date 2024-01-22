import unittest
from unittest.mock import patch, Mock

import fleet_management_api.api_impl.obj_to_db as obj_to_db
from fleet_management_api.models import (
    Car,
    MobilePhone,
    CarState,
    GNSSPosition,
    Order,
    OrderState,
    PlatformHwId,
    Route,
    Stop
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


class Test_Creating_Car_State_DB_Model(unittest.TestCase):

    def test_creating_car_state_db_model_from_car_state_object_preserves_attribute_values(self):
        car_state = CarState(id=12, status="idle", car_id=1, speed=7, fuel=8, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        car_state_db_model = obj_to_db.car_state_to_db_model(car_state)
        self.assertEqual(car_state_db_model.id, car_state.id)
        self.assertEqual(car_state_db_model.status, car_state.status)
        self.assertEqual(car_state_db_model.car_id, car_state.car_id)
        self.assertEqual(car_state_db_model.speed, car_state.speed)
        self.assertEqual(car_state_db_model.fuel, car_state.fuel)
        self.assertEqual(car_state_db_model.position, car_state.position.to_dict())

    def test_creating_car_state_db_model_from_car_state_object_with_only_required_attributes_specified_preserves_attribute_values(self):
        car_state = CarState(id=12, status="idle", car_id=1)
        car_state_db_model = obj_to_db.car_state_to_db_model(car_state)
        self.assertEqual(car_state_db_model.id, car_state.id)
        self.assertEqual(car_state_db_model.status, car_state.status)
        self.assertEqual(car_state_db_model.car_id, car_state.car_id)
        self.assertEqual(car_state_db_model.speed, car_state.speed)
        self.assertEqual(car_state_db_model.fuel, car_state.fuel)
        self.assertEqual(car_state_db_model.position, car_state.position)

    def test_car_state_converted_to_db_model_and_back_is_unchanged(self):
        state_in = CarState(id=12, status="idle", car_id=1)
        state_out = obj_to_db.car_state_from_db_model(obj_to_db.car_state_to_db_model(state_in))
        self.assertEqual(state_out, state_in)

    def test_car_state_with_all_attributes_specified_converted_to_db_model_and_back_is_unchanged(self):
        state_in = CarState(id=12, status="idle", car_id=1, speed=7, fuel=8, position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50))
        state_out = obj_to_db.car_state_from_db_model(obj_to_db.car_state_to_db_model(state_in))
        self.assertEqual(state_out, state_in)


class Test_Creating_Order_DB_Model(unittest.TestCase):

    def test_creating_db_model_from_order_preserves_attribute_values(self):
        order = Order(id=1, user_id=789, car_id=12, target_stop_id=7, stop_route_id=8)
        order_db_model = obj_to_db.order_to_db_model(order)
        self.assertEqual(order_db_model.id, order.id)
        self.assertEqual(order_db_model.priority, order.priority)
        self.assertEqual(order_db_model.user_id, order.user_id)
        self.assertEqual(order_db_model.car_id, order.car_id)
        self.assertEqual(order_db_model.target_stop_id, order.target_stop_id)
        self.assertEqual(order_db_model.stop_route_id, order.stop_route_id)
        self.assertEqual(order_db_model.notification_phone, order.notification_phone)

    def test_creating_db_model_from_order_with_only_required_attributes_specified_preserves_attribute_values(self):
        order = Order(
            id=1,
            priority="normal",
            user_id=789,
            car_id=12,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        order_db_model = obj_to_db.order_to_db_model(order)
        self.assertEqual(order_db_model.id, order.id)
        self.assertEqual(order_db_model.priority, order.priority)
        self.assertEqual(order_db_model.user_id, order.user_id)
        self.assertEqual(order_db_model.car_id, order.car_id)
        self.assertEqual(order_db_model.target_stop_id, order.target_stop_id)
        self.assertEqual(order_db_model.stop_route_id, order.stop_route_id)
        self.assertEqual(order_db_model.notification_phone, order.notification_phone.to_dict())

    def test_order_converted_to_db_model_and_back_is_unchanged(self):
        order_in = Order(id=1, user_id=789, car_id=12, target_stop_id=7, stop_route_id=8)
        order_out = obj_to_db.order_from_db_model(obj_to_db.order_to_db_model(order_in))
        self.assertEqual(order_out, order_in)

    def test_order_with_all_attributes_specified_converted_to_db_model_and_back_is_unchanged(self):
        order_in = Order(
            id=1,
            priority="high",
            user_id=789,
            car_id=12,
            target_stop_id=7,
            stop_route_id=8,
            notification_phone=MobilePhone(phone='1234567890')
        )
        order_out = obj_to_db.order_from_db_model(obj_to_db.order_to_db_model(order_in))
        self.assertEqual(order_out, order_in)


class Test_Creating_Platform_HW_Id_DB_Model(unittest.TestCase):

    def test_creating_db_model_from_paltform_hw_id_preserves_attribute_values(self):
        platform_hwid = PlatformHwId(id=1, name="test_platform")
        platform_db_model = obj_to_db.platform_hw_id_to_db_model(platform_hwid)
        self.assertEqual(platform_db_model.id, platform_hwid.id)
        self.assertEqual(platform_db_model.name, platform_hwid.name)

    def test_platform_hwid_converted_to_db_model_and_back_preserves_its_attributes(self):
        platform_hwid_in = PlatformHwId(id=1, name="test_platform")
        platform_hwid_out = obj_to_db.platform_hw_id_from_db_model(
            obj_to_db.platform_hw_id_to_db_model(platform_hwid_in)
        )
        self.assertEqual(platform_hwid_out, platform_hwid_in)


class Test_Creating_RouteDBModel(unittest.TestCase):

    def test_creating_db_model_from_route_preserves_attribute_values(self):
        route = Route(id=1, name="test_route")
        route_db_model = obj_to_db.route_to_db_model(route)
        self.assertEqual(route_db_model.id, route.id)
        self.assertEqual(route_db_model.name, route.name)

    def test_route_converted_to_db_model_and_back_preserves_its_attributes(self):
        route_in = Route(id=1, name="test_route")
        route_out = obj_to_db.route_from_db_model(obj_to_db.route_to_db_model(route_in))
        self.assertEqual(route_out, route_in)


class Test_Creating_StopDBModel(unittest.TestCase):

    def test_creating_db_model_from_stop_preserves_attribute_values(self):
        stop = Stop(
            id=1,
            name="test_stop",
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
            notification_phone=MobilePhone(phone='1234567890')
        )
        stop_db_model = obj_to_db.stop_to_db_model(stop)
        self.assertEqual(stop_db_model.id, stop.id)
        self.assertEqual(stop_db_model.name, stop.name)
        self.assertEqual(stop_db_model.position, stop.position.to_dict())
        self.assertEqual(stop_db_model.notification_phone, stop.notification_phone.to_dict())

    def test_stop_converted_to_db_model_and_back_preserves_its_attributes(self):
        stop_in = Stop(
            id=1,
            name="test_stop",
            position=GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50),
            notification_phone=MobilePhone(phone='1234567890')
        )
        stop_out = obj_to_db.stop_from_db_model(obj_to_db.stop_to_db_model(stop_in))
        self.assertEqual(stop_out, stop_in)


class Test_Creating_OrderStateDBModel(unittest.TestCase):

    def test_creating_db_model_from_order_state_preserves_attribute_values(self):
        order_state = OrderState(id=1, status="to_accept", order_id=1)
        order_state_db_model = obj_to_db.order_state_to_db_model(order_state)
        self.assertEqual(order_state_db_model.id, order_state.id)
        self.assertEqual(order_state_db_model.status, order_state.status)
        self.assertEqual(order_state_db_model.order_id, order_state.order_id)
        self.assertEqual(order_state_db_model.timestamp, order_state.timestamp)

    def test_order_state_converted_to_db_model_and_back_preserves_its_attributes(self):
        order_state_in = OrderState(id=1, status="to_accept", order_id=1)
        order_state_out = obj_to_db.order_state_from_db_model(obj_to_db.order_state_to_db_model(order_state_in))
        self.assertEqual(order_state_out, order_state_in)

    @patch('fleet_management_api.database.timestamp.timestamp_in_ms')
    def test_order_state_db_model_has_timestamp_attribute_corresponding_to_time_of_the_instances_creation(self, mock_timestamp_in_ms: Mock):
        mock_timestamp_in_ms.return_value(1234567890)
        order_state = OrderState(id=1, status="to_accept", order_id=1)
        order_state_db_model = obj_to_db.order_state_to_db_model(order_state)
        self.assertEqual(order_state_db_model.timestamp, 1234567890)


if __name__=="__main__":
    unittest.main() # pragma: no cover
