from __future__ import annotations
from typing import ClassVar, List
import dataclasses

import sqlalchemy as _sqa
from sqlalchemy.orm import Mapped as _Mapped
from sqlalchemy.orm import DeclarativeBase as _DeclarativeBase
from sqlalchemy.orm import mapped_column as _mapped_column
from sqlalchemy.orm import relationship as _relationship


DATABASE_URL = "sqlite:///:memory:"


class Base(_DeclarativeBase):
    def copy(self) -> Base:
        return self.__class__(
            **{col.name: getattr(self, col.name) for col in self.__table__.columns}
        )


@dataclasses.dataclass
class PlatformHWDBModel(Base):
    __tablename__ = "platform_hw"
    id: _Mapped[int] = _mapped_column(
        _sqa.Integer, primary_key=True, unique=True, nullable=False
    )
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    cars: _Mapped[List["CarDBModel"]] = _relationship("CarDBModel", lazy="noload")

    def __repr__(self) -> str:
        return f"PlatformHW(id={self.id}, name={self.name})"


@dataclasses.dataclass
class CarDBModel(Base):
    __tablename__ = "cars"
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    car_admin_phone: _Mapped[dict] = _mapped_column(_sqa.JSON, nullable=True)
    default_route_id: _Mapped[int] = _mapped_column(_sqa.Integer, nullable=True)
    platform_hw_id: _Mapped[int] = _mapped_column(
        _sqa.ForeignKey("platform_hw.id"), nullable=False, unique=True
    )
    under_test: _Mapped[bool] = _mapped_column(_sqa.Boolean, nullable=False)

    platformhw: _Mapped["PlatformHWDBModel"] = _relationship(
        "PlatformHWDBModel", back_populates="cars", lazy="noload"
    )
    states: _Mapped[List["CarStateDBModel"]] = _relationship(
        "CarStateDBModel", cascade="save-update, merge, delete", back_populates="car"
    )
    orders: _Mapped[List["OrderDBModel"]] = _relationship(
        "OrderDBModel", back_populates="car"
    )

    def __repr__(self) -> str:
        return (
            f"Car(id={self.id}, name={self.name}, platform_hw_id={self.platform_hw_id})"
        )


@dataclasses.dataclass
class CarStateDBModel(Base):
    __tablename__ = "car_states"
    _max_n_of_states: ClassVar[int] = 50
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    status: _Mapped[str] = _mapped_column(_sqa.String)
    car_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("cars.id"), nullable=False)
    speed: _Mapped[float] = _mapped_column(_sqa.Float)
    fuel: _Mapped[int] = _mapped_column(_sqa.Integer)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    timestamp: _Mapped[int] = _mapped_column(
        _sqa.BigInteger
    )  # this attribute serves for auto-removal of car old states

    car: _Mapped[CarDBModel] = _relationship(
        "CarDBModel", back_populates="states", lazy="noload"
    )

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return (
            f"CarState(id={self.id}, car_id={self.car_id}, status={self.status}, speed={self.speed}, "
            f"fuel={self.fuel}, position={self.position}, timestamp={self.timestamp})"
        )


@dataclasses.dataclass
class OrderDBModel(Base):
    __tablename__ = "orders"
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    priority: _Mapped[str] = _mapped_column(_sqa.String)
    user_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    target_stop_id: _Mapped[int] = _mapped_column(
        _sqa.ForeignKey("stops.id"), nullable=False
    )
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
    car: _Mapped["CarDBModel"] = _relationship(
        "CarDBModel", back_populates="orders", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"Order(id={self.id}, priority={self.priority}, user_id={self.user_id}, car_id={self.car_id}, target_stop_id={self.target_stop_id}, stop_route_id={self.stop_route_id}, notification_phone={self.notification_phone})"


@dataclasses.dataclass
class OrderStateDBModel(Base):
    __tablename__ = "order_states"
    _max_n_of_states: ClassVar[int] = 50
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    status: _Mapped[str] = _mapped_column(_sqa.String)
    timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)
    order_id: _Mapped[int] = _mapped_column(
        _sqa.ForeignKey("orders.id"), nullable=False
    )
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
        return f"OrderState(id={self.id}, order_id={self.order_id}, status={self.status}, timestamp={self.timestamp})"


@dataclasses.dataclass
class StopDBModel(Base):
    __tablename__ = "stops"
    id: _Mapped[int] = _mapped_column(
        _sqa.Integer, primary_key=True, unique=True, autoincrement=True
    )
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    notification_phone: _Mapped[dict] = _mapped_column(_sqa.JSON)

    orders: _Mapped[List["OrderDBModel"]] = _relationship(
        "OrderDBModel", back_populates="target_stop"
    )

    def __repr__(self) -> str:
        return f"Stop(id={self.id}, name={self.name}, position={self.position}, notification_phone={self.notification_phone})"


@dataclasses.dataclass
class RouteDBModel(Base):
    __tablename__ = "routes"
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    stop_ids: _Mapped[object] = _mapped_column(_sqa.PickleType)

    route_points: _Mapped[object] = _relationship(
        "RoutePointsDBModel",
        cascade="save-update, merge, delete",
        back_populates="route",
    )

    def __repr__(self) -> str:
        return f"Route(id={self.id}, name={self.name}, stop_ids={self.stop_ids})"


@dataclasses.dataclass
class RoutePointsDBModel(Base):
    __tablename__ = "route_points"
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    points: _Mapped[object] = _mapped_column(_sqa.PickleType)
    route: _Mapped[RouteDBModel] = _relationship(
        "RouteDBModel", back_populates="route_points", lazy="noload"
    )
    route_id: _Mapped[int] = _mapped_column(
        _sqa.ForeignKey("routes.id"), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"RoutePoints(id={self.id}, route_id={self.route_id}, points={self.points})"
        )


@dataclasses.dataclass
class ApiKeyDBModel(Base):
    __tablename__ = "api_keys"
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    key: _Mapped[str] = _mapped_column(_sqa.String, unique=True, nullable=True)
    creation_timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)

    def __repr__(self) -> str:
        return f"ApiKey(id={self.id}, name={self.name}, creation_timestamp={self.creation_timestamp})"
