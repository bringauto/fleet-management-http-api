import dataclasses

from sqlalchemy import Integer, String, Engine
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


@dataclasses.dataclass
class TestBase(Base):
    __tablename__ = 'test'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    test_str: Mapped[str] = mapped_column(String)
    test_int: Mapped[int] = mapped_column(Integer)


@dataclasses.dataclass
class TestBase2(Base):
    __tablename__ = 'test_2'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_str_2: Mapped[str] = mapped_column(String)
    test_int_2: Mapped[int] = mapped_column(Integer)


def initialize_test_tables(connection_engine: Engine|None) -> None:
    if connection_engine is None:
        raise RuntimeError("Database connection not set up.")
    Base.metadata.create_all(connection_engine)