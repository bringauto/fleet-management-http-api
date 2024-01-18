import unittest

from fleet_management_api.app import get_app
from fleet_management_api.database.connection import set_test_connection_source
from fleet_management_api.models import PlatformHwId


class Test_Creating_Platform_HW_Id(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_creating_platform_hw_id(self):
        platform_hw_id = PlatformHwId(id=5, name="test_platform")
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json=platform_hw_id.to_dict())
            self.assertEqual(response.status_code, 200)

    def test_creating_platform_hw_id_with_already_taken_id_returns_code_400(self):
        platform_hw_id_1 = PlatformHwId(id=1, name="test_platform_1")
        platform_hw_id_2 = PlatformHwId(id=1, name="test_platform_2")
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json=platform_hw_id_1.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/platformhwid', json=platform_hw_id_2 .to_dict())
            self.assertEqual(response.status_code, 400)

    def test_creating_platform_hw_id_with_already_taken_name_returns_code_400(self):
        platform_hw_id_1 = PlatformHwId(id=1, name="test_platform")
        platform_hw_id_2 = PlatformHwId(id=516515, name="test_platform")
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json=platform_hw_id_1.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/platformhwid', json=platform_hw_id_2 .to_dict())
            self.assertEqual(response.status_code, 400)

    def test_creating_platform_hw_id_with_missing_id_or_name_returns_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json={"name": "test_platform"})
            self.assertEqual(response.status_code, 400)
            response = c.post('/v1/platformhwid', json={"id": 1})
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main() # pragma: no coverages