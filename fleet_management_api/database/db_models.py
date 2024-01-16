import dataclasses

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


@dataclasses.dataclass
class CarDBModel(Base):
    __tablename__ = 'cars'
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
    platform_id: Mapped[int] = Column(Integer)
    car_admin_phone: Mapped[str] = Column(String)
    default_route_id: Mapped[int] = Column(Integer)

