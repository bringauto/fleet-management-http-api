import dataclasses

import fleet_management_api.models as _models
from fleet_management_api.app import TestApp, TEST_TENANT_NAME
from fleet_management_api.database.timestamp import timestamp_ms


@dataclasses.dataclass
class TenantFromTokenMock:
    current: str = ""
    all: list[str] = dataclasses.field(default_factory=list)

    @property
    def unrestricted(self) -> bool:
        return not self.current and not self.all


def create_platform_hws(
    app: TestApp, count: int = 1, tenant: str = TEST_TENANT_NAME, api_key: str = ""
) -> None:
    with app.app.test_client(tenant) as c:
        c.set_cookie("localhost", "tenant", tenant)
        for i in range(count):
            platformhw = _models.PlatformHW(name=f"Test Platform Hw {timestamp_ms()+i}")
            if api_key:
                response = c.post(f"/v2/management/platformhw?api_key={api_key}", json=[platformhw])
            else:
                response = c.post("/v2/management/platformhw", json=[platformhw])
            assert response.status_code == 200, f"Failed to create platform HW: {response.json}"


def create_stops(app: TestApp, count: int = 1, tenant: str = TEST_TENANT_NAME) -> None:
    with app.app.test_client(tenant) as c:
        c.set_cookie("localhost", "tenant", tenant)
        for i in range(count):
            stop = _models.Stop(
                name=f"Test Stop {timestamp_ms()+i}",
                position=_models.GNSSPosition(latitude=49, longitude=17, altitude=300),
            )
            c.post("/v2/management/stop", json=[stop])


def create_route(app: TestApp, stop_ids: tuple[int, ...], tenant: str = TEST_TENANT_NAME) -> None:
    with app.app.test_client(tenant) as c:
        c.set_cookie("localhost", "tenant", tenant)
        route = _models.Route(name=f"test_route_{timestamp_ms()}", stop_ids=stop_ids)
        c.post("/v2/management/route", json=[route])
