import fleet_management_api.models as _models
from fleet_management_api.app import _TestApp
from fleet_management_api.database.timestamp import timestamp_ms


def create_platform_hws(app: _TestApp, count: int = 1) -> None:
    with app.app.test_client() as c:
        for i in range(count):
            platformhw = _models.PlatformHW(name=f"Test Platform Hw {timestamp_ms()+i}")
            c.post("/v2/management/platformhw", json=platformhw)


def create_stops(app: _TestApp, count: int = 1) -> None:
    with app.app.test_client() as c:
        for i in range(count):
            stop = _models.Stop(
                name=f"Test Stop {timestamp_ms()+i}",
                position=_models.GNSSPosition(latitude=49, longitude=17, altitude=300),
            )
            c.post("/v2/management/stop", json=stop)


def create_route(app: _TestApp, stop_ids: tuple[int,...]) -> None:
    with app.app.test_client() as c:
        route = _models.Route(name=f"test_route_{timestamp_ms()}", stop_ids=stop_ids)
        c.post("/v2/management/route", json=route)