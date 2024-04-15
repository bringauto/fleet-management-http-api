from __future__ import annotations
from typing import Optional

import sqlalchemy as _sqa
from sqlalchemy.orm import Mapped as _Mapped
from sqlalchemy.orm import DeclarativeBase as _DeclarativeBase
from sqlalchemy.orm import mapped_column as _mapped_column
from sqlalchemy.orm import relationship as _relationship


OrderId = int


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
    model_name = "PlatformHW"
    __tablename__ = "platform_hw"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    cars: _Mapped[list["CarDBModel"]] = _relationship("CarDBModel", lazy="noload")

    def __repr__(self) -> str:
        return f"PlatformHW(ID={self.id}, name={self.name})"


class CarDBModel(Base):
    model_name = "Car"
    __tablename__ = "cars"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    platform_hw_id: _Mapped[int] = _mapped_column(
        _sqa.ForeignKey("platform_hw.id"), nullable=False, unique=True
    )
    car_admin_phone: _Mapped[Optional[dict]] = _mapped_column(_sqa.JSON)
    default_route_id: _Mapped[Optional[int]] = _mapped_column(
        _sqa.ForeignKey("routes.id"), nullable=True
    )
    under_test: _Mapped[bool] = _mapped_column(_sqa.Boolean, nullable=False)

    platformhw: _Mapped["PlatformHWDBModel"] = _relationship(
        "PlatformHWDBModel", back_populates="cars", lazy="noload"
    )
    states: _Mapped[list["CarStateDBModel"]] = _relationship(
        "CarStateDBModel", cascade="save-update, merge, delete", back_populates="car"
    )
    orders: _Mapped[list["OrderDBModel"]] = _relationship("OrderDBModel", back_populates="car")
    default_route: _Mapped["RouteDBModel"] = _relationship(
        "RouteDBModel", lazy="noload", back_populates="cars"
    )

    def __repr__(self) -> str:
        return f"Car(ID={self.id}, name={self.name}, platform_hw_ID={self.platform_hw_id})"


class CarStateDBModel(Base):
    model_name = "CarState"
    __tablename__ = "car_states"
    _max_n_of_states: int = 50
    car_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("cars.id"), nullable=False)
    status: _Mapped[str] = _mapped_column(_sqa.String)
    speed: _Mapped[float] = _mapped_column(_sqa.Float)
    fuel: _Mapped[int] = _mapped_column(_sqa.Integer)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)

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
    model_name = "Order"
    __tablename__ = "orders"
    priority: _Mapped[str] = _mapped_column(_sqa.String)
    user_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)
    target_stop_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("stops.id"), nullable=False)
    stop_route_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    notification_phone: _Mapped[dict] = _mapped_column(_sqa.JSON)
    updated: _Mapped[bool] = _mapped_column(_sqa.Boolean)
    car_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("cars.id"), nullable=False)

    states: _Mapped[list["OrderStateDBModel"]] = _relationship(
        "OrderStateDBModel",
        cascade="save-update, merge, delete",
        back_populates="order",
    )
    target_stop: _Mapped["StopDBModel"] = _relationship(
        "StopDBModel", back_populates="orders", lazy="noload"
    )
    car: _Mapped["CarDBModel"] = _relationship("CarDBModel", back_populates="orders", lazy="noload")
    active_orders: set[OrderId] = set()

    def __repr__(self) -> str:
        return (
            f"Order(ID={self.id}, priority={self.priority}, user_ID={self.user_id}, "
            f"car_ID={self.car_id}, target_stop_ID={self.target_stop_id}, "
            f"stop_route_ID={self.stop_route_id}, notification_phone={self.notification_phone})"
        )


class OrderStateDBModel(Base):
    model_name = "OrderState"
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
    model_name = "Stop"
    __tablename__ = "stops"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    notification_phone: _Mapped[dict] = _mapped_column(_sqa.JSON)

    orders: _Mapped[list["OrderDBModel"]] = _relationship(
        "OrderDBModel", back_populates="target_stop"
    )

    def __repr__(self) -> str:
        return f"Stop(ID={self.id}, name={self.name}, position={self.position}, notification_phone={self.notification_phone})"


class RouteDBModel(Base):
    model_name = "Route"
    __tablename__ = "routes"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    stop_ids: _Mapped[object] = _mapped_column(_sqa.PickleType)

    cars: _Mapped[list[CarDBModel]] = _relationship("CarDBModel", back_populates="default_route")
    route_visualization: _Mapped[object] = _relationship(
        "RouteVisualizationDBModel",
        cascade="save-update, merge, delete",
        back_populates="route",
    )

    def __repr__(self) -> str:
        return f"Route(ID={self.id}, name={self.name}, stop_ids={self.stop_ids})"


class RouteVisualizationDBModel(Base):
    model_name = "RouteVisualization"
    __tablename__ = "route_visualization"
    points: _Mapped[object] = _mapped_column(_sqa.PickleType)
    hexcolor: _Mapped[str] = _mapped_column(_sqa.String, nullable=True)
    route: _Mapped[RouteDBModel] = _relationship(
        "RouteDBModel", back_populates="route_visualization", lazy="noload"
    )
    route_id: _Mapped[int] = _mapped_column(_sqa.ForeignKey("routes.id"), nullable=False)

    def __repr__(self) -> str:
        return f"RouteVisualization (ID={self.id}, route_ID={self.route_id}, points={self.points})"


class ApiKeyDBModel(Base):
    model_name = "ApiKey"
    __tablename__ = "api_keys"
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    key: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    creation_timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)

    def __repr__(self) -> str:
        return (
            f"ApiKey(ID={self.id}, name={self.name}, creation_timestamp={self.creation_timestamp})"
        )
