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




