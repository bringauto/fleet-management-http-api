from typing import ClassVar
import dataclasses

from sqlalchemy import Integer, String, JSON, Boolean, BigInteger, Float
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


DATABASE_URL = "sqlite:///:memory:"


class Base(DeclarativeBase):
    pass


@dataclasses.dataclass
class CarDBModel(Base):
    __tablename__ = 'cars'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    platform_id: Mapped[int] = mapped_column(Integer)
    car_admin_phone: Mapped[dict] = mapped_column(JSON, nullable=True)
    default_route_id: Mapped[int] = mapped_column(Integer, nullable=True)


@dataclasses.dataclass
class CarStateDBModel(Base):
    __tablename__ = 'car_states'
    _max_n_of_states: ClassVar[int] = 50
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    status: Mapped[str] = mapped_column(String)
    car_id: Mapped[int] = mapped_column(Integer)
    speed: Mapped[float] = mapped_column(Float)
    fuel: Mapped[int] = mapped_column(Integer)
    position: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[int] = mapped_column(BigInteger)

    @classmethod
    def max_n_of_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_number_of_stored_states(cls, n: int) -> None:
        if n>0:
            cls._max_n_of_states = n


@dataclasses.dataclass
class OrderDBModel(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    priority: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer)
    car_id: Mapped[int] = mapped_column(Integer)
    target_stop_id: Mapped[int] = mapped_column(Integer)
    stop_route_id: Mapped[int] = mapped_column(Integer)
    notification_phone: Mapped[dict] = mapped_column(JSON)
    updated: Mapped[bool] = mapped_column(Boolean)


@dataclasses.dataclass
class PlatformHwIdDBModel(Base):
    __tablename__ = 'platform_hw_ids'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)


@dataclasses.dataclass
class RouteDBModel(Base):
    __tablename__ = 'routes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)


@dataclasses.dataclass
class StopDBModel(Base):
    __tablename__ = 'stops'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    position: Mapped[dict] = mapped_column(JSON)
    notification_phone: Mapped[dict] = mapped_column(JSON)


@dataclasses.dataclass
class OrderStateDBModel(Base):
    __tablename__ = 'order_states'
    _max_n_of_states: ClassVar[int] = 50
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    status: Mapped[str] = mapped_column(String)
    order_id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[int] = mapped_column(BigInteger)

    @classmethod
    def max_n_of_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_number_of_stored_states(cls, n: int) -> None:
        if n>0:
            cls._max_n_of_states = n