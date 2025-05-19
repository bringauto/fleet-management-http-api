from __future__ import annotations
from typing import Optional, Protocol

from sqlalchemy import (
    Boolean,
    BigInteger,
    Float,
    ForeignKey,
    Integer,
    JSON,
    PickleType,
    String,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Session, Mapped, DeclarativeBase, mapped_column, relationship

from fleet_management_api.api_impl.tenants import TenantNotAccessible as _TenantNotAccessible


OrderId = int


TENANTS_ID_COLUMN = "tenants.id"
CARS_ID_COLUMN = "cars.id"
TENANT_ID_NAME = "tenant_id"
TENANT_NAME = "tenants.name"
CASCADE = "save-update, merge, delete"


def _unique_name_under_tenant(table_name: str) -> UniqueConstraint:
    """Return a UniqueConstraint for a table that contains items owned by a tenant and that has a `name` column.
    The item name must be unique under a tenant and can be repeated across tenants.
    """
    return UniqueConstraint(TENANT_ID_NAME, "name", name=f"name_under_tenant_{table_name}")


class SessionWithTenants(Session):

    def __init__(self, *args, tenants: Tenants, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenants = tenants

    @property
    def tenants(self) -> Tenants:
        return self._tenants

    @classmethod
    def object_session(cls, instance) -> SessionWithTenants:
        return super().object_session(instance)


class Tenants(Protocol):
    """Protocol for a class that provides the current tenant and all accessible tmptyenants."""

    @property
    def current(self) -> str: ...

    @property
    def all(self) -> list[str]: ...

    @property
    def unrestricted(self) -> bool: ...

    def is_accessible(self, tenant_name: str) -> bool: ...


class Base(DeclarativeBase):
    """Base class for all ORM-mapped classes. It applies declarative mapping to all the subclasses
    derived from this class.
    """

    model_name: str = "Base"
    state: bool = False

    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, unique=True, nullable=False
    )

    def copy(self) -> Base:
        return self.__class__(
            **{col.name: getattr(self, col.name) for col in self.__table__.columns}
        )

    @classmethod
    def owned_by_tenant(cls) -> bool:
        return hasattr(cls, "tenant_id")


class TenantDB(Base):
    """ORM-mapped class representing a tenant in the database."""

    model_name = "Tenant"
    __tablename__ = "tenants"
    name: Mapped[str] = mapped_column(String, unique=True)

    platform_hw: Mapped[list[PlatformHWDB]] = relationship("PlatformHWDB", lazy="select")
    cars: Mapped[list[CarDB]] = relationship("CarDB", lazy="select")
    car_states: Mapped[list[CarStateDB]] = relationship("CarStateDB", lazy="select")
    car_action_states: Mapped[list[CarActionStateDB]] = relationship(
        "CarActionStateDB", lazy="select"
    )
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
    test_items: Mapped[list[TestItem]] = relationship(
        "TestItem", lazy="select", back_populates="tenant"
    )

    def __repr__(self) -> str:
        return f"Tenant(ID={self.id}, name={self.name})"


class PlatformHWDB(Base):
    """ORM-mapped class representing a platform hardware in the database."""

    model_name = "PlatformHW"
    __tablename__ = "platform_hw"
    __table_args__ = (_unique_name_under_tenant(__tablename__),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="platform_hw", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String)
    cars: Mapped[list[CarDB]] = relationship("CarDB", lazy="noload")

    def __repr__(self) -> str:
        return f"PlatformHW(id={self.id}, name={self.name})"


class CarDB(Base):
    """ORM-mapped class representing a car in the database."""

    model_name = "Car"
    __tablename__ = "cars"
    __table_args__ = (_unique_name_under_tenant(__tablename__),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="cars", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String)
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
    action_states: Mapped[list["CarActionStateDB"]] = relationship(
        "CarActionStateDB", cascade="save-update, merge, delete", back_populates="car"
    )
    orders: Mapped[list["OrderDB"]] = relationship("OrderDB", back_populates="car")
    default_route: Mapped["RouteDB"] = relationship("RouteDB", lazy="noload", back_populates="cars")

    def __repr__(self) -> str:
        return f"Car(id={self.id}, name={self.name}, platform_hw_ID={self.platform_hw_id})"


class CarStateDB(Base):
    """ORM-mapped class representing a car state in the database."""

    model_name = "CarState"
    state = True
    __tablename__ = "car_states"
    _max_n_of_states: int = 50

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="car_states", lazy="noload", foreign_keys=[tenant_id]
    )

    car_id: Mapped[int] = mapped_column(ForeignKey(CARS_ID_COLUMN), nullable=False)
    car: Mapped[CarDB] = relationship("CarDB", back_populates="states", lazy="select")

    status: Mapped[str] = mapped_column(String)
    speed: Mapped[float] = mapped_column(Float)
    fuel: Mapped[int] = mapped_column(Integer)
    position: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[int] = mapped_column(BigInteger)

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return (
            f"CarState(id={self.id}, car_id={self.car_id}, status={self.status}, speed={self.speed}, "
            f"fuel={self.fuel}, position={self.position}, timestamp={self.timestamp})"
        )


class CarActionStateDB(Base):
    """ORM-mapped class representing a car action state in the database."""

    model_name = "CarActionState"
    state = True
    __tablename__ = "car_action_states"
    _max_n_of_states: int = 50

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="car_action_states", lazy="noload", foreign_keys=[tenant_id]
    )

    car_id: Mapped[int] = mapped_column(ForeignKey(CARS_ID_COLUMN), nullable=False)
    status: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(BigInteger)

    car: Mapped[CarDB] = relationship("CarDB", back_populates="action_states", lazy="select")

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return f"CarActionState(id={self.id}, car_id={self.car_id}, status={self.status}, timestamp={self.timestamp})"


class OrderDB(Base):
    """ORM-mapped class representing an order in the database."""

    model_name = "Order"
    __tablename__ = "orders"

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="orders", lazy="noload", foreign_keys=[tenant_id]
    )

    priority: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(BigInteger)
    target_stop_id: Mapped[int] = mapped_column(ForeignKey("stops.id"), nullable=False)
    stop_route_id: Mapped[int] = mapped_column(Integer)
    notification_phone: Mapped[dict] = mapped_column(JSON)
    car_id: Mapped[int] = mapped_column(ForeignKey(CARS_ID_COLUMN), nullable=False)

    is_visible: Mapped[bool] = mapped_column(Boolean)
    states: Mapped[list[OrderStateDB]] = relationship(
        "OrderStateDB", cascade=CASCADE, back_populates="order"
    )
    target_stop: Mapped[StopDB] = relationship("StopDB", back_populates="orders", lazy="noload")
    car: Mapped[CarDB] = relationship("CarDB", back_populates="orders", lazy="noload")

    def __repr__(self) -> str:
        return (
            f"Order(id={self.id}, priority={self.priority}, is_visible={self.is_visible}, "
            f"car_id={self.car_id}, target_stop_ID={self.target_stop_id}, "
            f"stop_route_ID={self.stop_route_id}, notification_phone={self.notification_phone})"
        )


class OrderStateDB(Base):
    """ORM-mapped class representing an order state in the database."""

    model_name = "OrderState"
    state = True
    __tablename__ = "order_states"
    _max_n_of_states: int = 50

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="order_states", lazy="noload", foreign_keys=[tenant_id]
    )

    status: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(BigInteger)
    car_id: Mapped[int] = mapped_column(Integer)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped[OrderDB] = relationship("OrderDB", back_populates="states", lazy="noload")

    @classmethod
    def max_n_of_stored_states(cls) -> int:
        return cls._max_n_of_states

    @classmethod
    def set_max_n_of_stored_states(cls, n: int) -> None:
        if n > 0:
            cls._max_n_of_states = n

    def __repr__(self) -> str:
        return f"OrderState(id={self.id}, order_ID={self.order_id}, status={self.status}, timestamp={self.timestamp})"


class StopDB(Base):
    """ORM-mapped class representing a stop in the database."""

    model_name = "Stop"
    __tablename__ = "stops"
    __table_args__ = (_unique_name_under_tenant(__tablename__),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="stops", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String)
    position: Mapped[dict] = mapped_column(JSON)
    notification_phone: Mapped[dict] = mapped_column(JSON)
    is_auto_stop: Mapped[bool] = mapped_column(Boolean)
    orders: Mapped[list[OrderDB]] = relationship("OrderDB", back_populates="target_stop")

    def __repr__(self) -> str:
        return f"Stop(id={self.id}, name={self.name}, position={self.position}, notification_phone={self.notification_phone})"


class RouteDB(Base):
    """ORM-mapped class representing a route in the database."""

    model_name = "Route"
    __tablename__ = "routes"
    __table_args__ = (_unique_name_under_tenant(__tablename__),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="routes", lazy="noload", foreign_keys=[tenant_id]
    )
    name: Mapped[str] = mapped_column(String)
    stop_ids: Mapped[object] = mapped_column(PickleType)
    cars: Mapped[list[CarDB]] = relationship("CarDB", back_populates="default_route")
    visualization: Mapped[object] = relationship(
        "RouteVisualizationDB",
        cascade=CASCADE,
        back_populates="route",
    )

    def __repr__(self) -> str:
        return f"Route(id={self.id}, name={self.name}, stop_ids={self.stop_ids})"


class RouteVisualizationDB(Base):
    """ORM-mapped class representing a route visualization in the database."""

    model_name = "RouteVisualization"
    __tablename__ = "route_visualization"
    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="route_visualizations", lazy="noload", foreign_keys=[tenant_id]
    )
    points: Mapped[object] = mapped_column(PickleType)
    hexcolor: Mapped[str] = mapped_column(String, nullable=True)
    route: Mapped[RouteDB] = relationship("RouteDB", back_populates="visualization", lazy="noload")
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)

    def __repr__(self) -> str:
        return f"RouteVisualization (id={self.id}, route_ID={self.route_id}, points={self.points})"


class ApiKeyDB(Base):
    """ORM-mapped class representing an API key in the database."""

    model_name = "ApiKey"
    __tablename__ = "api_keys"
    name: Mapped[str] = mapped_column(String, unique=True)
    key: Mapped[str] = mapped_column(String, unique=True)
    creation_timestamp: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return (
            f"ApiKey(id={self.id}, name={self.name}, creation_timestamp={self.creation_timestamp})"
        )


class TestItem(Base):
    """ORM-mapped class representing a test item in the database."""

    model_name = "TestItem"
    __tablename__ = "test_item"
    tenant_id: Mapped[int] = mapped_column(ForeignKey(TENANTS_ID_COLUMN), nullable=False)
    tenant: Mapped[TenantDB] = relationship(
        "TenantDB", back_populates="test_items", lazy="noload", foreign_keys=[tenant_id]
    )
    test_str: Mapped[str] = mapped_column(String)
    test_int: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"TestItem(ID={self.id}, test_str={self.test_str}, test_int={self.test_int})"


# Event listener to set tenant_id before insert or update
@event.listens_for(CarStateDB, "before_insert")
def set_car_state_tenant_id(mapper, connection, target):
    _use_ref_tenant_id(mapper, connection, target, "car_id", CarDB)


# Event listener to set tenant_id before insert or update
@event.listens_for(CarActionStateDB, "before_insert")
def set_car_action_state_tenant_id(mapper, connection, target):
    _use_ref_tenant_id(mapper, connection, target, "car_id", CarDB)


# Event listener to set tenant_id before insert or update
@event.listens_for(OrderStateDB, "before_insert")
def set_order_state_tenant_id(mapper, connection, target):
    _use_ref_tenant_id(mapper, connection, target, "order_id", OrderDB)


def _use_ref_tenant_id(mapper: Base, connection, target, ref_id: str, ref_base: type[Base]):
    session = SessionWithTenants.object_session(target)
    if session:
        ref = session.query(ref_base).filter_by(id=getattr(target, ref_id)).one()
        assert hasattr(ref, "tenant_id"), f"Reference {ref_base} does not have tenant_id."
        tenant_id = ref.tenant_id
        tenant = session.query(TenantDB).filter_by(id=tenant_id).one()
        if tenant:
            if session.tenants.is_accessible(tenant.name):
                target.tenant_id = ref.tenant_id
            else:
                raise _TenantNotAccessible(f"Tenant '{tenant.name}' is not accessible.")
        else:
            raise ValueError(f"Tenant with ID {tenant_id} not found.")
