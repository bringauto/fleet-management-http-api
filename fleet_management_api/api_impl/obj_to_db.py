import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.timestamp as _tstamp


def car_to_db_model(car: _models.Car) -> _db_models.CarDBModel:
    if car.car_admin_phone is None:
        car_mobile_phone = None
    else:
        car_mobile_phone = car.car_admin_phone.to_dict()
    return _db_models.CarDBModel(
        id=car.id,
        name=car.name,
        platform_hw_id=car.platform_hw_id,
        car_admin_phone=car_mobile_phone,
        default_route_id=car.default_route_id
    )


def car_from_db_model(car_db_model: _db_models.CarDBModel) -> _models.Car:
    if car_db_model.car_admin_phone is None:
        car_mobile_phone = None
    else:
        car_mobile_phone = _models.MobilePhone.from_dict(car_db_model.car_admin_phone)
    return _models.Car(
        id=car_db_model.id,
        name=car_db_model.name,
        platform_hw_id=car_db_model.platform_hw_id,
        car_admin_phone=car_mobile_phone,
        default_route_id=car_db_model.default_route_id
    )


def car_state_to_db_model(car_state: _models.CarState) -> _db_models.CarStateDBModel:
    if car_state.position is None:
        car_position = None
    else:
        car_position = car_state.position.to_dict()
    timestamp = timestamp=_tstamp.timestamp_ms()
    return _db_models.CarStateDBModel(
        id=car_state.id,
        status=str(car_state.status),
        car_id=car_state.car_id,
        speed=car_state.speed,
        fuel=car_state.fuel,
        position=car_position,
        timestamp=timestamp
    )


def car_state_from_db_model(car_state_db_model: _db_models.CarStateDBModel) -> _models.CarState:
    if car_state_db_model.position is None:
        car_position = None
    else:
        car_position = _models.GNSSPosition.from_dict(car_state_db_model.position)
    return _models.CarState(
        id=car_state_db_model.id,
        status=car_state_db_model.status,
        car_id=car_state_db_model.car_id,
        speed=car_state_db_model.speed,
        fuel=car_state_db_model.fuel,
        position=car_position
    )


def order_to_db_model(order: _models.Order) -> _db_models.OrderDBModel:
    if order.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = order.notification_phone.to_dict()
    return _db_models.OrderDBModel(
        id=order.id,
        priority=order.priority,
        user_id=order.user_id,
        car_id=order.car_id,
        target_stop_id=order.target_stop_id,
        stop_route_id=order.stop_route_id,
        notification_phone=notification_phone,
        updated=True
    )


def order_from_db_model(order_db_model: _db_models.OrderDBModel) -> _models.Order:
    if order_db_model.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = _models.MobilePhone.from_dict(order_db_model.notification_phone)
    return _models.Order(
        id=order_db_model.id,
        priority=order_db_model.priority,
        user_id=order_db_model.user_id,
        car_id=order_db_model.car_id,
        target_stop_id=order_db_model.target_stop_id,
        stop_route_id=order_db_model.stop_route_id,
        notification_phone=notification_phone,
    )


def order_state_to_db_model(order_state: _models.OrderState) -> _db_models.OrderStateDBModel:
    return _db_models.OrderStateDBModel(
        id=order_state.id,
        status=str(order_state.status),
        order_id=order_state.order_id,
        timestamp=_tstamp.timestamp_ms()
    )


def order_state_from_db_model(order_state_db_model: _db_models.OrderStateDBModel) -> _models.OrderState:
    return _models.OrderState(
        id=order_state_db_model.id,
        status=order_state_db_model.status,
        order_id=order_state_db_model.order_id
    )


def platform_hw_id_to_db_model(platform_hw_id: _models.PlatformHwId) -> _db_models.PlatformHwIdDBModel:
    return _db_models.PlatformHwIdDBModel(
        id=platform_hw_id.id,
        name=platform_hw_id.name
    )


def platform_hw_id_from_db_model(platform_hw_id_db_model: _db_models.PlatformHwIdDBModel) -> _models.PlatformHwId:
    return _models.PlatformHwId(
        id = platform_hw_id_db_model.id,
        name = platform_hw_id_db_model.name
    )


def route_to_db_model(route: _models.Route) -> _db_models.RouteDBModel:
    return _db_models.RouteDBModel(
        id=route.id,
        name=route.name,
        stop_ids=route.stop_ids
    )


def route_from_db_model(route_db_model: _db_models.RouteDBModel) -> _models.Route:
    return _models.Route(
        id=route_db_model.id,
        name=route_db_model.name,
        stop_ids=route_db_model.stop_ids
    )


def route_points_to_db_model(route_points: _models.RoutePoints) -> _db_models.RoutePointsDBModel:
    return _db_models.RoutePointsDBModel(
        id=route_points.id,
        route_id=route_points.route_id,
        points=route_points.points
    )


def route_points_from_db_model(route_points_db_model: _db_models.RoutePointsDBModel) -> _models.RoutePoints:
    return _models.RoutePoints(
        id=route_points_db_model.id,
        route_id=route_points_db_model.route_id,
        points=route_points_db_model.points
    )


def stop_to_db_model(stop: _models.Stop) -> _db_models.StopDBModel:
    if stop.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = stop.notification_phone.to_dict()
    return _db_models.StopDBModel(
        id=stop.id,
        name=stop.name,
        position=stop.position.to_dict(),
        notification_phone=notification_phone
    )


def stop_from_db_model(stop_db_model: _db_models.StopDBModel) -> _models.Stop:
    if stop_db_model.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = _models.MobilePhone.from_dict(stop_db_model.notification_phone)
    return _models.Stop(
        id=stop_db_model.id,
        name=stop_db_model.name,
        position=_models.GNSSPosition.from_dict(stop_db_model.position),
        notification_phone=notification_phone
    )

