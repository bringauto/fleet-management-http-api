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
            response = c.post('/v1/platformhwid', json=platform_hw_id)
            self.assertEqual(response.status_code, 200)

    def test_creating_platform_hw_id_with_already_taken_id_returns_code_400(self):
        platform_hw_id_1 = PlatformHwId(id=1, name="test_platform_1")
        platform_hw_id_2 = PlatformHwId(id=1, name="test_platform_2")
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json=platform_hw_id_1)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/platformhwid', json=platform_hw_id_2)
            self.assertEqual(response.status_code, 400)

    def test_creating_platform_hw_id_with_already_taken_name_returns_code_400(self):
        platform_hw_id_1 = PlatformHwId(id=1, name="test_platform")
        platform_hw_id_2 = PlatformHwId(id=516515, name="test_platform")
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json=platform_hw_id_1)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/platformhwid', json=platform_hw_id_2)
            self.assertEqual(response.status_code, 400)

    def test_creating_platform_hw_id_with_missing_id_or_name_returns_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json={"name": "test_platform"})
            self.assertEqual(response.status_code, 400)
            response = c.post('/v1/platformhwid', json={"id": 1})
            self.assertEqual(response.status_code, 400)


class Test_Retrieving_Platform_HW_Id(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_retrieving_existing_platform_hw_ids(self):
        platform_hw_id_1 = PlatformHwId(id=1, name="test_platform_1")
        platform_hw_id_2 = PlatformHwId(id=2, name="test_platform_2")
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json=platform_hw_id_1)
            response = c.post('/v1/platformhwid', json=platform_hw_id_2)
            response = c.get('/v1/platformhwid')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_retrieving_platform_hw_ids_when_no_hw_id_exists_yields_empty_list(self):
        # no platform hw id has been sent to the database
        with self.app.test_client() as c:
            response = c.get('/v1/platformhwid')
            self.assertEqual(response.status_code, 200)
            self.assertListEqual(response.json, [])


class Test_Getting_Single_Platform_HW_Id(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_getting_single_existing_platform_hw_id(self):
        platform_hw_id_1 = PlatformHwId(id=15, name="test_platform_y")
        platform_hw_id_2 = PlatformHwId(id=24, name="test_platform_z")
        with self.app.test_client() as c:
            c.post('/v1/platformhwid', json=platform_hw_id_1)
            c.post('/v1/platformhwid', json=platform_hw_id_2)

            response = c.get('/v1/platformhwid/15')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["id"], 15)

            response = c.get('/v1/platformhwid/24')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["id"], 24)

    def test_retrieving_nonexistent_platform_hw_id_yields_code_404(self):
        nonexistent_platform_id = 156155
        with self.app.test_client() as c:
            response = c.get(f'/v1/platformhwid/{nonexistent_platform_id}')
            self.assertEqual(response.status_code, 404)


class Test_Deleting_Platform_HW_Id(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_deleting_an_existing_platform_hw_id(self):
        platform_hw_id = PlatformHwId(id=123, name="test_platform")
        with self.app.test_client() as c:
            c.post('/v1/platformhwid', json=platform_hw_id)
            response = c.delete('/v1/platformhwid/123')
            self.assertEqual(response.status_code, 200)

            response = c.get('/v1/platformhwid')
            self.assertEqual(response.json, [])

    def test_deleting_a_nonexistent_platform_hw_id_yields_code_404(self):
        nonexistent_platform_id = 156155
        with self.app.test_client() as c:
            response = c.delete(f'/v1/platformhwid/{nonexistent_platform_id}')
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main() # pragma: no coverages