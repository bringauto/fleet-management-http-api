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

    def is_accessible(self, tenant_name: str) -> bool:
        return not (self.all) or tenant_name in self.all


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


def create_stops(
    app: TestApp, count: int = 1, tenant: str = TEST_TENANT_NAME, api_key: str = ""
) -> list[int]:
    ids = []
    with app.app.test_client(tenant) as c:
        c.set_cookie("localhost", "tenant", tenant)
        for i in range(count):
            stop = _models.Stop(
                name=f"Test Stop {timestamp_ms()+i}",
                position=_models.GNSSPosition(latitude=49, longitude=17, altitude=300),
            )
            response = c.post(f"/v2/management/stop?api_key={api_key}", json=[stop])
            assert response.status_code == 200, f"Failed to create stop: {response.json}"
            assert response.json is not None
            ids.append(response.json[0]["id"])
    return ids


def create_route(
    app: TestApp, stop_ids: tuple[int, ...], tenant: str = TEST_TENANT_NAME, api_key: str = ""
) -> None:
    with app.app.test_client(tenant) as c:
        c.set_cookie("localhost", "tenant", tenant)
        route = _models.Route(name=f"test_route_{timestamp_ms()}", stop_ids=stop_ids)
        c.post(f"/v2/management/route?api_key={api_key}", json=[route])
