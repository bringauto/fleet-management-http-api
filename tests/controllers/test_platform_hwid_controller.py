import unittest

from fleet_management_api.app import get_app
from fleet_management_api.database.connection import set_test_connection_source
from fleet_management_api.models import Order


class Test_Creating_Platform_HW_Id(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_creating_platform_hw_id(self):
        platform_hw_id = Order(id=5, name="test_platform")
        with self.app.test_client() as c:
            response = c.post('/v1/platformhwid', json=platform_hw_id.to_dict())
            self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main() # pragma: no coverages