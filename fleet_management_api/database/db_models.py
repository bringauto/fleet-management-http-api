from typing import ClassVar
import dataclasses

import sqlalchemy as _sqa
from sqlalchemy.orm import Mapped as _Mapped
from sqlalchemy.orm import DeclarativeBase as _DeclarativeBase
from sqlalchemy.orm import mapped_column as _mapped_column


DATABASE_URL = "sqlite:///:memory:"


class Base(_DeclarativeBase):
    pass


@dataclasses.dataclass
class CarDBModel(Base):
    __tablename__ = 'cars'
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    platform_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    car_admin_phone: _Mapped[dict] = _mapped_column(_sqa.JSON, nullable=True)
    default_route_id: _Mapped[int] = _mapped_column(_sqa.Integer, nullable=True)


@dataclasses.dataclass
class CarStateDBModel(Base):
    __tablename__ = 'car_states'
    _max_n_of_states: ClassVar[int] = 50
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    status: _Mapped[str] = _mapped_column(_sqa.String)
    car_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    speed: _Mapped[float] = _mapped_column(_sqa.Float)
    fuel: _Mapped[int] = _mapped_column(_sqa.Integer)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n>0:
            cls._max_n_of_states = n


@dataclasses.dataclass
class OrderDBModel(Base):
    __tablename__ = 'orders'
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    priority: _Mapped[str] = _mapped_column(_sqa.String)
    user_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    car_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    target_stop_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    stop_route_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    notification_phone: _Mapped[dict] = _mapped_column(_sqa.JSON)
    updated: _Mapped[bool] = _mapped_column(_sqa.Boolean)


@dataclasses.dataclass
class PlatformHwIdDBModel(Base):
    __tablename__ = 'platform_hw_ids'
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)


@dataclasses.dataclass
class RouteDBModel(Base):
    __tablename__ = 'routes'
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    stop_ids: _Mapped[object] = _mapped_column(_sqa.PickleType)


@dataclasses.dataclass
class RoutePointsDBModel(Base):
    __tablename__ = 'route_points'
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    route_id: _Mapped[int] = _mapped_column(_sqa.Integer, unique=True)
    points: _Mapped[object] = _mapped_column(_sqa.PickleType)


@dataclasses.dataclass
class StopDBModel(Base):
    __tablename__ = 'stops'
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    position: _Mapped[dict] = _mapped_column(_sqa.JSON)
    notification_phone: _Mapped[dict] = _mapped_column(_sqa.JSON)


@dataclasses.dataclass
class OrderStateDBModel(Base):
    __tablename__ = 'order_states'
    _max_n_of_states: ClassVar[int] = 50
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    status: _Mapped[str] = _mapped_column(_sqa.String)
    order_id: _Mapped[int] = _mapped_column(_sqa.Integer)
    timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n>0:
            cls._max_n_of_states = n


@dataclasses.dataclass
class ApiKeyDBModel(Base):
    __tablename__ = 'api_keys'
    id: _Mapped[int] = _mapped_column(_sqa.Integer, primary_key=True, unique=True)
    name: _Mapped[str] = _mapped_column(_sqa.String, unique=True)
    key: _Mapped[str] = _mapped_column(_sqa.String, unique=True, nullable=True)
    creation_timestamp: _Mapped[int] = _mapped_column(_sqa.BigInteger)
