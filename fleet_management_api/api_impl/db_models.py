from fleet_management_api.models import (
    Car,
    MobilePhone,
    CarState,
    GNSSPosition,
    Order
)
from fleet_management_api.database.db_models import CarDBModel, CarStateDBModel, OrderDBModel


def car_to_db_model(car: Car) -> CarDBModel:
    if car.car_admin_phone is None:
        car_mobile_phone = None
    else:
        car_mobile_phone = car.car_admin_phone.to_dict()
    return CarDBModel(
        id=car.id,
        name=car.name,
        platform_id=car.platform_id,
        car_admin_phone=car_mobile_phone,
        default_route_id=car.default_route_id
    )


def car_from_db_model(car_db_model: CarDBModel) -> Car:
    if car_db_model.car_admin_phone is None:
        car_mobile_phone = None
    else:
        car_mobile_phone = MobilePhone.from_dict(car_db_model.car_admin_phone)
    return Car(
        id=car_db_model.id,
        name=car_db_model.name,
        platform_id=car_db_model.platform_id,
        car_admin_phone=car_mobile_phone,
        default_route_id=car_db_model.default_route_id
    )


def car_state_to_db_model(car_state: CarState) -> CarStateDBModel:
    if car_state.position is None:
        car_position = None
    else:
        car_position = car_state.position.to_dict()
    return CarStateDBModel(
        id=car_state.id,
        status=car_state.status,
        car_id=car_state.car_id,
        speed=car_state.speed,
        fuel=car_state.fuel,
        position=car_position
    )


def car_state_from_db_model(car_state_db_model: CarStateDBModel) -> CarState:
    if car_state_db_model.position is None:
        car_position = None
    else:
        car_position = GNSSPosition.from_dict(car_state_db_model.position)
    return CarState(
        id=car_state_db_model.id,
        status=car_state_db_model.status,
        car_id=car_state_db_model.car_id,
        speed=car_state_db_model.speed,
        fuel=car_state_db_model.fuel,
        position=car_position
    )


def order_to_db_model(order: Order) -> OrderDBModel:
    if order.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = order.notification_phone.to_dict()
    return OrderDBModel(
        id=order.id,
        priority=order.priority,
        user_id=order.user_id,
        status=order.status,
        car_id=order.car_id,
        target_stop_id=order.target_stop_id,
        stop_route_id=order.stop_route_id,
        notification_phone=notification_phone
    )


def order_from_db_model(order_db_model: OrderDBModel) -> Order:
    if order_db_model.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = MobilePhone.from_dict(order_db_model.notification_phone)
    return Order(
        id=order_db_model.id,
        priority=order_db_model.priority,
        user_id=order_db_model.user_id,
        status=order_db_model.status,
        car_id=order_db_model.car_id,
        target_stop_id=order_db_model.target_stop_id,
        stop_route_id=order_db_model.stop_route_id,
        notification_phone=notification_phone
    )