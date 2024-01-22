import dataclasses

from sqlalchemy import Column, Integer, String, Engine
from sqlalchemy.orm import Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


@dataclasses.dataclass
class TestBase(Base):
    __tablename__ = 'test'
    id: Mapped[int] = Column(Integer, primary_key=True, unique=True)
    test_str: Mapped[str] = Column(String)
    test_int: Mapped[int] = Column(Integer)


@dataclasses.dataclass
class TestBase2(Base):
    __tablename__ = 'test_2'
    id: Mapped[int] = Column(Integer, primary_key=True)
    test_str_2: Mapped[str] = Column(String)
    test_int_2: Mapped[int] = Column(Integer)


def initialize_test_tables(connection_engine: Engine) -> None:
    Base.metadata.create_all(connection_engine)