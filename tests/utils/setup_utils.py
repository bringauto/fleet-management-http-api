import fleet_management_api.models as _models
from fleet_management_api.app import _TestApp


def create_platform_hws(app: _TestApp, *ids: int):
    with app.app.test_client() as c:
        for id in ids:
            platformhw = _models.PlatformHW(id=id, name=f"Test Platform Hw {id}")
            c.post('/v2/management/platformhw', json=platformhw)


def create_stops(app: _TestApp, *stop_ids: int) -> None:
    with app.app.test_client() as c:
        for stop_id in stop_ids:
            stop = _models.Stop(id=stop_id, name=f"Test Stop {stop_id}", position=_models.GNSSPosition(latitude=49, longitude=17, altitude=300))
            c.post('/v2/management/stop', json=stop)