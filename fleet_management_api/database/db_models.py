import dataclasses

from sqlalchemy import Column, Integer, String, JSON, Boolean, BigInteger
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


DATABASE_URL = "sqlite:///:memory:"


class Base(DeclarativeBase):
    pass


@dataclasses.dataclass
class CarDBModel(Base):
    __tablename__ = 'cars'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = Column(String, unique=True)
    platform_id: Mapped[int] = Column(Integer)
    car_admin_phone: Mapped[dict] = mapped_column(JSON)
    default_route_id: Mapped[int] = Column(Integer)


@dataclasses.dataclass
class CarStateDBModel(Base):
    __tablename__ = 'car_states'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    status: Mapped[str] = Column(String)
    car_id: Mapped[int] = Column(Integer)
    speed: Mapped[int] = Column(Integer)
    fuel: Mapped[int] = Column(Integer)
    position: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[int] = Column(BigInteger, unique=True)


@dataclasses.dataclass
class OrderDBModel(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    priority: Mapped[str] = Column(String)
    user_id: Mapped[int] = Column(Integer)
    car_id: Mapped[int] = Column(Integer)
    target_stop_id: Mapped[int] = Column(Integer)
    stop_route_id: Mapped[int] = Column(Integer)
    notification_phone: Mapped[dict] = mapped_column(JSON)
    updated: Mapped[bool] = Column(Boolean)


@dataclasses.dataclass
class PlatformHwIdDBModel(Base):
    __tablename__ = 'platform_hw_ids'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = Column(String, unique=True)


@dataclasses.dataclass
class RouteDBModel(Base):
    __tablename__ = 'routes'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = Column(String, unique=True)


@dataclasses.dataclass
class StopDBModel(Base):
    __tablename__ = 'stops'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = Column(String, unique=True)
    position: Mapped[dict] = mapped_column(JSON)
    notification_phone: Mapped[dict] = mapped_column(JSON)


@dataclasses.dataclass
class OrderStateDBModel(Base):
    __tablename__ = 'order_states'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    status: Mapped[str] = Column(String)
    order_id: Mapped[int] = Column(Integer)
    timestamp: Mapped[int] = Column(BigInteger, unique=True)

    @classmethod
    @property
    def max_n_of_states(cls) -> int:
        return 50
