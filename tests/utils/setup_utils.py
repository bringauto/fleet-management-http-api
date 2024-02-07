import fleet_management_api.models as _models
from fleet_management_api.app import _TestApp


def create_platform_hw_ids(app: _TestApp, *ids: int):
    with app.app.test_client() as c:
        for id in ids:
            platformhwid = _models.PlatformHwId(id=id, name=f"Test Platform Hw Id {id}")
            c.post('/v2/management/platformhwid', json=platformhwid)


def create_stops(app: _TestApp, *stop_ids: int) -> None:
    with app.app.test_client() as c:
        for stop_id in stop_ids:
            stop = _models.Stop(id=stop_id, name=f"Test Stop {stop_id}", position=_models.GNSSPosition(latitude=49, longitude=17, altitude=300))
            c.post('/v2/management/stop', json=stop)