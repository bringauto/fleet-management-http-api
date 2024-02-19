from __future__ import annotations
from typing import List, Optional, Dict

import sqlalchemy as _sqa
from sqlalchemy.orm import Mapped as _Mapped
from sqlalchemy.orm import DeclarativeBase as _DeclarativeBase
from sqlalchemy.orm import mapped_column as _mapped_column
from sqlalchemy.orm import relationship as _relationship


class Base(_DeclarativeBase):
    model_name: str = "Base"
    id: _Mapped[Optional[int]] = _mapped_column(
        _sqa.Integer, primary_key=True, unique=True, nullable=False
    )

    def copy(self) -> Base:
        return self.__class__(
            **{col.name: getattr(self, col.name) for col in self.__table__.columns}
        )


class PlatformHWDBModel(Base):
    __modelname__ = "PlatformHW"
    __tablename__ = "platform_hw"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    cars: _Mapped[List["CarDBModel"]] = _relationship("CarDBModel", lazy="noload")

    def __repr__(self) -> str:
        return f"PlatformHW(ID={self.id}, name={self.name})"


class CarDBModel(Base):
    __modelname__ = "Car"
    __tablename__ = "cars"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    platform_hw_id: _Mapped[int] = _mapped_column(
        _sqa.ForeignKey("platform_hw.id"), nullable=False, unique=True
    )
    car_admin_phone: _Mapped[Optional[Dict]] = _mapped_column(_sqa.JSON)
    default_route_id: _Mapped[Optional[int]] = _mapped_column(
        _sqa.ForeignKey("routes.id"), nullable=True
    )
    under_test: _Mapped[bool] = _mapped_column(_sqa.Boolean, nullable=False)

    platformhw: _Mapped["PlatformHWDBModel"] = _relationship(
        "PlatformHWDBModel", back_populates="cars", lazy="noload"
    )
    states: _Mapped[List["CarStateDBModel"]] = _relationship(
        "CarStateDBModel", cascade="save-update, merge, delete", back_populates="car"
    )
    orders: _Mapped[List["OrderDBModel"]] = _relationship("OrderDBModel", back_populates="car")
    default_route: _Mapped["RouteDBModel"] = _relationship(
        "RouteDBModel", lazy="noload", back_populates="cars"
    )

    def __repr__(self) -> str:
        return f"Car(ID={self.id}, name={self.name}, platform_hw_ID={self.platform_hw_id})"


class CarStateDBModel(Base):
    __modelname__ = "CarState"
    __tablename__ = "car_states"
    _max_n_of_states: int = 50
    car_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("cars.id"), nullable=False)
    status: _Mapped[str] = _mapped_column(_sqa.String)
    speed: _Mapped[float] = _mapped_column(_sqa.Float)
    fuel: _Mapped[int] = _mapped_column(_sqa.Integer)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    timestamp: _Mapped[int] = _mapped_column(
        _sqa.BigInteger
    )  # timestamp attribute serves for auto-removal of old states

    car: _Mapped[CarDBModel] = _relationship("CarDBModel", back_populates="states", lazy="noload")

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return (
            f"CarState(ID={self.id}, car_ID={self.car_id}, status={self.status}, speed={self.speed}, "
            f"fuel={self.fuel}, position={self.position}, timestamp={self.timestamp})"
        )


class OrderDBModel(Base):
    __modelname__ = "Order"
    __tablename__ = "orders"
    priority: _Mapped[str] = _mapped_column(_sqa.String)
    user_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    target_stop_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("stops.id"), nullable=False)
    stop_route_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    notification_phone: _Mapped[dict] = _mapped_column(_sqa.JSON)
    updated: _Mapped[bool] = _mapped_column(_sqa.Boolean)
    car_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("cars.id"), nullable=False)

    states: _Mapped[List["OrderStateDBModel"]] = _relationship(
        "OrderStateDBModel",
        cascade="save-update, merge, delete",
        back_populates="order",
    )
    target_stop: _Mapped["StopDBModel"] = _relationship(
        "StopDBModel", back_populates="orders", lazy="noload"
    )
    car: _Mapped["CarDBModel"] = _relationship("CarDBModel", back_populates="orders", lazy="noload")

    def __repr__(self) -> str:
        return (
            f"Order(ID={self.id}, priority={self.priority}, user_ID={self.user_id}, car_ID={self.car_id}, "
            f"target_stop_ID={self.target_stop_id}, stop_route_ID={self.stop_route_id}, "
            f"notification_phone={self.notification_phone})"
        )


class OrderStateDBModel(Base):
    __modelname__ = "OrderState"
    __tablename__ = "order_states"
    _max_n_of_states: int = 50
    status: _Mapped[str] = _mapped_column(_sqa.String)
    timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)
    order_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("orders.id"), nullable=False)
    order: _Mapped[OrderDBModel] = _relationship(
        "OrderDBModel", back_populates="states", lazy="noload"
    )

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return f"OrderState(ID={self.id}, order_ID={self.order_id}, status={self.status}, timestamp={self.timestamp})"


class StopDBModel(Base):
    __modelname__ = "Stop"
    __tablename__ = "stops"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    notification_phone: _Mapped[dict] = _mapped_column(_sqa.JSON)

    orders: _Mapped[List["OrderDBModel"]] = _relationship(
        "OrderDBModel", back_populates="target_stop"
    )

    def __repr__(self) -> str:
        return f"Stop(ID={self.id}, name={self.name}, position={self.position}, notification_phone={self.notification_phone})"


class RouteDBModel(Base):
    __modelname__ = "Route"
    __tablename__ = "routes"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    stop_ids: _Mapped[object] = _mapped_column(_sqa.PickleType)

    cars: _Mapped[List[CarDBModel]] = _relationship("CarDBModel", back_populates="default_route")
    route_points: _Mapped[object] = _relationship(
        "RoutePointsDBModel",
        cascade="save-update, merge, delete",
        back_populates="route",
    )

    def __repr__(self) -> str:
        return f"Route(ID={self.id}, name={self.name}, stop_ids={self.stop_ids})"


class RoutePointsDBModel(Base):
    __modelname__ = "RoutePoints"
    __tablename__ = "route_points"
    points: _Mapped[object] = _mapped_column(_sqa.PickleType)
    route: _Mapped[RouteDBModel] = _relationship(
        "RouteDBModel", back_populates="route_points", lazy="noload"
    )
    route_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("routes.id"), nullable=False)

    def __repr__(self) -> str:
        return f"RoutePoints(ID={self.id}, route_ID={self.route_id}, points={self.points})"


class ApiKeyDBModel(Base):
    __modelname__ = "ApiKey"
    __tablename__ = "api_keys"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    key: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    creation_timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)

    def __repr__(self) -> str:
        return (
            f"ApiKey(ID={self.id}, name={self.name}, creation_timestamp={self.creation_timestamp})"
        )
