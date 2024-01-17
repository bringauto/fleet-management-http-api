from fleet_management_api.models import Car, MobilePhone
from fleet_management_api.database.db_models import CarDBModel


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