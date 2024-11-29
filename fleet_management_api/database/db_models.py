from __future__ import annotations
from typing import Optional

from sqlalchemy import Boolean, BigInteger, Float, ForeignKey, Integer, JSON, PickleType, String
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship


OrderId = int


TENANT_ID = "tenants.id"
CASCADE = "save-update, merge, delete"


class Base(DeclarativeBase):
    model_name: str = "Base"
    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, unique=True, nullable=False
    )

    def copy(self) -> Base:
        return self.__class__(
            **{col.name: getattr(self, col.name) for col in self.__table__.columns}
        )


class TenantDB(Base):
    model_name = "Tenant"
    __tablename__ = "tenants"
    name: Mapped[str] = mapped_column(String, unique=True)

    platform_hw: Mapped[list[PlatformHWDB]] = relationship("PlatformHWDB", lazy="select")
    cars: Mapped[list[CarDB]] = relationship("CarDB", lazy="select")
    car_states: Mapped[list[CarStateDB]] = relationship("CarStateDB", lazy="select")
    orders: Mapped[list[OrderDB]] = relationship(
        "OrderDB", lazy="select", foreign_keys="OrderDB.tenant_id"
    )
    order_states: Mapped[list[OrderStateDB]] = relationship(
        "OrderStateDB", lazy="select", foreign_keys="OrderStateDB.tenant_id"
    )
    stops: Mapped[list[StopDB]] = relationship("StopDB", lazy="select")
    routes: Mapped[list[RouteDB]] = relationship(
        "RouteDB", lazy="select", foreign_keys="RouteDB.tenant_id"
    )
    route_visualizations: Mapped[list[RouteVisualizationDB]] = relationship(
        "RouteVisualizationDB", lazy="select", foreign_keys="RouteVisualizationDB.tenant_id"
    )
    test_items: Mapped[list[PlatformHWDB]] = relationship(
        "TestItem", lazy="select", back_populates="tenant"
    )

    def __repr__(self) -> str:
        return f"Tenant(ID={self.id}, name={self.name})"


class PlatformHWDB(Base):
    model_name = "PlatformHW"
    __tablename__ = "platform_hw"
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="platform_hw", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String, unique=True)
    cars: Mapped[list[CarDB]] = relationship("CarDB", lazy="noload")

    def __repr__(self) -> str:
        return f"PlatformHW(ID={self.id}, name={self.name})"


class CarDB(Base):
    model_name = "Car"
    __tablename__ = "cars"
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="cars", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String, unique=True)
    platform_hw_id: Mapped[int] = mapped_column(
        ForeignKey("platform_hw.id"), nullable=False, unique=True
    )
    car_admin_phone: Mapped[Optional[dict]] = mapped_column(JSON)
    default_route_id: Mapped[Optional[int]] = mapped_column(ForeignKey("routes.id"), nullable=True)
    under_test: Mapped[bool] = mapped_column(Boolean, nullable=False)
    platformhw: Mapped[PlatformHWDB] = relationship(
        "PlatformHWDB", back_populates="cars", lazy="noload"
    )
    states: Mapped[list[CarStateDB]] = relationship(
        "CarStateDB", cascade=CASCADE, back_populates="car"
    )
    orders: Mapped[list[OrderDB]] = relationship("OrderDB", back_populates="car")
    default_route: Mapped[RouteDB] = relationship("RouteDB", lazy="noload", back_populates="cars")

    def __repr__(self) -> str:
        return f"Car(ID={self.id}, name={self.name}, platform_hw_ID={self.platform_hw_id})"


class CarStateDB(Base):
    model_name = "CarState"
    __tablename__ = "car_states"
    _max_n_of_states: int = 50
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="car_states", lazy="noload", foreign_keys=[tenant_id]
    )
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), nullable=False)
    status: Mapped[str] = mapped_column(String)
    speed: Mapped[float] = mapped_column(Float)
    fuel: Mapped[int] = mapped_column(Integer)
    position: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[int] = mapped_column(BigInteger)
    car: Mapped[CarDB] = relationship("CarDB", back_populates="states", lazy="select")

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return (
            f"CarState(ID={self.id}, car_ID={self.car_id}, status={self.status}, speed={self.speed}, "
            f"fuel={self.fuel}, position={self.position}, timestamp={self.timestamp})"
        )


class OrderDB(Base):
    model_name = "Order"
    __tablename__ = "orders"
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="orders", lazy="noload", foreign_keys=[tenant_id]
    )
    priority: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(BigInteger)
    target_stop_id: Mapped[int] = mapped_column(ForeignKey("stops.id"), nullable=False)
    stop_route_id: Mapped[int] = mapped_column(Integer)
    notification_phone: Mapped[dict] = mapped_column(JSON)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean)
    states: Mapped[list[OrderStateDB]] = relationship(
        "OrderStateDB", cascade=CASCADE, back_populates="order"
    )
    target_stop: Mapped[StopDB] = relationship("StopDB", back_populates="orders", lazy="noload")
    car: Mapped[CarDB] = relationship("CarDB", back_populates="orders", lazy="noload")

    def __repr__(self) -> str:
        return (
            f"Order(ID={self.id}, priority={self.priority}, is_visible={self.is_visible}, "
            f"car_ID={self.car_id}, target_stop_ID={self.target_stop_id}, "
            f"stop_route_ID={self.stop_route_id}, notification_phone={self.notification_phone})"
        )


class OrderStateDB(Base):
    model_name = "OrderState"
    __tablename__ = "order_states"
    _max_n_of_states: int = 50
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="order_states", lazy="noload", foreign_keys=[tenant_id]
    )
    status: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(BigInteger)
    car_id: Mapped[int] = mapped_column(Integer)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped[OrderDB] = relationship("OrderDB", back_populates="states", lazy="noload")
    tenant_name: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return f"OrderState(ID={self.id}, order_ID={self.order_id}, status={self.status}, timestamp={self.timestamp})"


class StopDB(Base):
    model_name = "Stop"
    __tablename__ = "stops"
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="stops", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String, unique=True)
    position: Mapped[dict] = mapped_column(JSON)
    notification_phone: Mapped[dict] = mapped_column(JSON)
    is_auto_stop: Mapped[bool] = mapped_column(Boolean)
    orders: Mapped[list[OrderDB]] = relationship("OrderDB", back_populates="target_stop")

    def __repr__(self) -> str:
        return f"Stop(ID={self.id}, name={self.name}, position={self.position}, notification_phone={self.notification_phone})"


class RouteDB(Base):
    model_name = "Route"
    __tablename__ = "routes"
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="routes", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String, unique=True)
    stop_ids: Mapped[object] = mapped_column(PickleType)
    tenant_name: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    cars: Mapped[list[CarDB]] = relationship("CarDB", back_populates="default_route")
    visualization: Mapped[object] = relationship(
        "RouteVisualizationDB",
        cascade=CASCADE,
        back_populates="route",
    )

    def __repr__(self) -> str:
        return f"Route(ID={self.id}, name={self.name}, stop_ids={self.stop_ids})"


class RouteVisualizationDB(Base):
    model_name = "RouteVisualization"
    __tablename__ = "route_visualization"
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="route_visualizations", lazy="noload", foreign_keys=[tenant_id]
    )
    points: Mapped[object] = mapped_column(PickleType)
    hexcolor: Mapped[str] = mapped_column(String, nullable=True)
    route: Mapped[RouteDB] = relationship("RouteDB", back_populates="visualization", lazy="noload")
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)

    def __repr__(self) -> str:
        return f"RouteVisualization (ID={self.id}, route_ID={self.route_id}, points={self.points})"


class ApiKeyDB(Base):
    model_name = "ApiKey"
    __tablename__ = "api_keys"
    name: Mapped[str] = mapped_column(String, unique=True)
    key: Mapped[str] = mapped_column(String, unique=True)
    creation_timestamp: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return (
            f"ApiKey(ID={self.id}, name={self.name}, creation_timestamp={self.creation_timestamp})"
        )


class TestItem(Base):
    model_name = "TestItem"
    __tablename__ = "test_item"
    tenant_id: Mapped[str] = mapped_column(ForeignKey(TENANT_ID), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="test_items", lazy="noload", foreign_keys=[tenant_id]
    )
    test_str: Mapped[str] = mapped_column(String)
    test_int: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"TestItem(ID={self.id}, test_str={self.test_str}, test_int={self.test_int})"
