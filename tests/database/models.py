from __future__ import annotations
from typing import List
import dataclasses

from sqlalchemy import Integer, String, Engine, ForeignKey
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship


class Base(DeclarativeBase):
    pass

    def copy(self) -> Base:
        return self.__class__(**{col.name: getattr(self, col.name) for col in self.__table__.columns})


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
    for table in Base.metadata.tables.values():
        table.create(connection_engine)


@dataclasses.dataclass
class ParentDBModel(Base):
    __tablename__ = 'parents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String)
    children: Mapped[List["ChildDBModel"]] = relationship("ChildDBModel", cascade='save-update, merge, delete', back_populates="parent")


@dataclasses.dataclass
class ChildDBModel(Base):
    __tablename__ = 'children'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id"), nullable=False)
    parent = relationship("ParentDBModel", back_populates="children", lazy="noload")