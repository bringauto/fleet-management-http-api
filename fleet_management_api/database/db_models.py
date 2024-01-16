import dataclasses

from sqlalchemy import Column, Integer, String, JSON
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
class TestBase(Base):
    __tablename__ = 'test'
    id: Mapped[int] = Column(Integer, primary_key=True)
    test_str: Mapped[str] = Column(String)
    test_int: Mapped[int] = Column(Integer)


@dataclasses.dataclass
class TestBase_2(Base):
    __tablename__ = 'test_2'
    id_2: Mapped[int] = Column(Integer, primary_key=True)
    test_str_2: Mapped[str] = Column(String)
    test_int_2: Mapped[int] = Column(Integer)



