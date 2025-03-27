from __future__ import annotations
from typing import Optional
import dataclasses

from sqlalchemy import Integer, String, Engine, inspect
from sqlalchemy.orm import Mapped, mapped_column
from fleet_management_api.database.db_models import Base, TestItem


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
        if not inspect(connection_engine).has_table(table.name):
            table.create(connection_engine)
