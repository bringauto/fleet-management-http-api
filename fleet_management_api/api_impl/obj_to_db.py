import fleet_management_api.models as _models
import fleet_management_api.database.db_models as _db_models
import fleet_management_api.database.timestamp as _tstamp


def car_to_db_model(car: _models.Car) -> _db_models.CarDB:
    car_admin_phone = car.car_admin_phone.to_dict() if car.car_admin_phone is not None else None
    return _db_models.CarDB(
        id=car.id,
        name=car.name,
        platform_hw_id=car.platform_hw_id,
        car_admin_phone=car_admin_phone,
        default_route_id=car.default_route_id,
        under_test=car.under_test,
    )


def car_from_db_model(
    car_db_model: _db_models.CarDB, last_state: _models.CarState | None
) -> _models.Car:
    return _models.Car(
        id=car_db_model.id,
        name=car_db_model.name,
        platform_hw_id=car_db_model.platform_hw_id,
        car_admin_phone=_models.MobilePhone.from_dict(car_db_model.car_admin_phone),
        default_route_id=car_db_model.default_route_id,
        under_test=car_db_model.under_test,
        last_state=last_state,
    )


def car_state_to_db_model(car_state: _models.CarState) -> _db_models.CarStateDB:
    if car_state.position is None:
        car_position = None
    else:
        car_position = car_state.position.to_dict()
    timestamp = _tstamp.timestamp_ms()
    return _db_models.CarStateDB(
        id=car_state.id,
        status=str(car_state.status),
        car_id=car_state.car_id,
        speed=car_state.speed,
        fuel=car_state.fuel,
        position=car_position,
        timestamp=timestamp,
    )


def car_state_from_db_model(
    car_state_db_model: _db_models.CarStateDB,
) -> _models.CarState:
    if car_state_db_model.position is None:
        car_position = None
    else:
        car_position = _models.GNSSPosition.from_dict(car_state_db_model.position)
    return _models.CarState(
        id=car_state_db_model.id,
        timestamp=car_state_db_model.timestamp,
        status=car_state_db_model.status,
        car_id=car_state_db_model.car_id,
        speed=car_state_db_model.speed,
        fuel=car_state_db_model.fuel,
        position=car_position,
    )


def car_action_state_to_db_model(
    car_action_state: _models.CarActionState,
) -> _db_models.CarActionStateDB:
    return _db_models.CarActionStateDB(
        id=car_action_state.id,
        status=str(car_action_state.action_status),
        car_id=car_action_state.car_id,
        timestamp=_tstamp.timestamp_ms(),
    )


def car_action_state_from_db_model(
    car_action_state_db_model: _db_models.CarActionStateDB,
) -> _models.CarActionState:
    assert isinstance(car_action_state_db_model, _db_models.CarActionStateDB), (
        f"Expected car_action_state_db_model to be of type _db_models.CarActionStateDB, "
        f"but got {type(car_action_state_db_model)}"
    )
    return _models.CarActionState(
        id=car_action_state_db_model.id,
        timestamp=car_action_state_db_model.timestamp,
        action_status=car_action_state_db_model.status,
        car_id=car_action_state_db_model.car_id,
    )


def order_to_db_model(order: _models.Order) -> _db_models.OrderDB:
    if order.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = order.notification_phone.to_dict()
    return _db_models.OrderDB(
        id=order.id,
        timestamp=_tstamp.timestamp_ms(),
        priority=order.priority,
        car_id=order.car_id,
        target_stop_id=order.target_stop_id,
        stop_route_id=order.stop_route_id,
        notification_phone=notification_phone,
        is_visible=order.is_visible,
    )


def order_from_db_model(
    order_db_model: _db_models.OrderDB, last_state: _models.OrderState | None
) -> _models.Order:

    if order_db_model.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = _models.MobilePhone.from_dict(order_db_model.notification_phone)
    return _models.Order(
        id=order_db_model.id,
        timestamp=order_db_model.timestamp,
        priority=order_db_model.priority,
        car_id=order_db_model.car_id,
        target_stop_id=order_db_model.target_stop_id,
        stop_route_id=order_db_model.stop_route_id,
        notification_phone=notification_phone,
        last_state=last_state,
        is_visible=order_db_model.is_visible,
    )


def order_state_to_db_model(
    order_state: _models.OrderState,
) -> _db_models.OrderStateDB:
    return _db_models.OrderStateDB(
        id=order_state.id,
        status=str(order_state.status),
        order_id=order_state.order_id,
        timestamp=_tstamp.timestamp_ms(),
    )


def order_state_from_db_model(
    order_state_db_model: _db_models.OrderStateDB,
) -> _models.OrderState:
    return _models.OrderState(
        id=order_state_db_model.id,
        status=order_state_db_model.status,
        order_id=order_state_db_model.order_id,
        timestamp=order_state_db_model.timestamp,
    )


def hw_to_db_model(
    platform_hw: _models.PlatformHW,
) -> _db_models.PlatformHWDB:
    return _db_models.PlatformHWDB(id=platform_hw.id, name=platform_hw.name)


def hw_from_db_model(
    platform_hw_db_model: _db_models.PlatformHWDB,
) -> _models.PlatformHW:
    return _models.PlatformHW(id=platform_hw_db_model.id, name=platform_hw_db_model.name)


def route_to_db_model(route: _models.Route) -> _db_models.RouteDB:
    return _db_models.RouteDB(id=route.id, name=route.name, stop_ids=route.stop_ids)


def route_from_db_model(route_db_model: _db_models.RouteDB) -> _models.Route:
    return _models.Route(
        id=route_db_model.id, name=route_db_model.name, stop_ids=route_db_model.stop_ids
    )


def route_visualization_to_db_model(
    route_visualization: _models.RouteVisualization,
) -> _db_models.RouteVisualizationDB:
    return _db_models.RouteVisualizationDB(
        id=route_visualization.id,
        route_id=route_visualization.route_id,
        points=route_visualization.points,
        hexcolor=route_visualization.hexcolor,
    )


def route_visualization_from_db_model(
    route_visualization_db_model: _db_models.RouteVisualizationDB,
) -> _models.RouteVisualization:
    return _models.RouteVisualization(
        id=route_visualization_db_model.id,
        route_id=route_visualization_db_model.route_id,
        points=route_visualization_db_model.points,
        hexcolor=route_visualization_db_model.hexcolor,
    )


def stop_to_db_model(stop: _models.Stop) -> _db_models.StopDB:
    if stop.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = stop.notification_phone.to_dict()
    position = stop.position.to_dict() if stop.position is not None else None
    return _db_models.StopDB(
        id=stop.id,
        name=stop.name,
        position=position,
        notification_phone=notification_phone,
        is_auto_stop=stop.is_auto_stop,
    )


def stop_from_db_model(stop_db_model: _db_models.StopDB) -> _models.Stop:
    if stop_db_model.notification_phone is None:
        notification_phone = None
    else:
        notification_phone = _models.MobilePhone.from_dict(stop_db_model.notification_phone)
    return _models.Stop(
        id=stop_db_model.id,
        name=stop_db_model.name,
        position=_models.GNSSPosition.from_dict(stop_db_model.position),
        notification_phone=notification_phone,
        is_auto_stop=stop_db_model.is_auto_stop,
    )


def tenant_to_db_model(
    tenant: _models.Tenant,
) -> _db_models.TenantDB:
    return _db_models.TenantDB(id=tenant.id, name=tenant.name)


def tenant_from_db_model(
    platform_hw_db_model: _db_models.TenantDB,
) -> _models.Tenant:
    return _models.Tenant(id=platform_hw_db_model.id, name=platform_hw_db_model.name)
