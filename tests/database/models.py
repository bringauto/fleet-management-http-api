from __future__ import annotations
from typing import Optional
import dataclasses

from sqlalchemy import Integer, String, Engine
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    model_name: str = "Base"

    def copy(self) -> Base:
        return self.__class__(
            **{col.name: getattr(self, col.name) for col in self.__table__.columns}
        )


@dataclasses.dataclass
class TestBase(Base):
    model_name: str = "TestBase"
    __tablename__ = "test"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    test_str: Mapped[str] = mapped_column(String)
    test_int: Mapped[int] = mapped_column(Integer)


@dataclasses.dataclass
class TestBase2(Base):
    model_name: str = "TestBase2"
    __tablename__ = "test_2"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_str_2: Mapped[str] = mapped_column(String)
    test_int_2: Mapped[int] = mapped_column(Integer)


def initialize_test_tables(connection_engine: Optional[Engine]) -> None:
    if connection_engine is None:
        raise RuntimeError("Database connection not set up.")
    for table in Base.metadata.tables.values():
        table.create(connection_engine)
