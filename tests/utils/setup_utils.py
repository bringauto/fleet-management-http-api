import fleet_management_api.models as _models
from fleet_management_api.app import _TestApp


def create_platform_hw_ids(app: _TestApp, *ids: int):
    with app.app.test_client() as c:
        for id in ids:
            platformhwid = _models.PlatformHwId(id=id, name=f"Test Platform Hw Id {id}")
            c.post('/v2/management/platformhwid', json=platformhwid)
