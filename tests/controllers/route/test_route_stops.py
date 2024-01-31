import os
import unittest

import fleet_management_api.app as _app
from fleet_management_api.database.connection import set_connection_source_test
from fleet_management_api.models import Route, Stop, GNSSPosition


class Test_Defining_Route_List_Of_Stops(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test("test_db.db")
        self.app = _app.get_test_app().app
        self.stop_A = Stop(id=1, name="test_stop_A", position=GNSSPosition(latitude=49, longitude=17, altitude=450))
        self.stop_B = Stop(id=2, name="test_stop_B", position=GNSSPosition(latitude=49.2, longitude=17, altitude=440))
        self.stop_C = Stop(id=3, name="test_stop_C", position=GNSSPosition(latitude=49.1, longitude=16.9, altitude=430))
        self.stop_D = Stop(id=4, name="test_stop_D", position=GNSSPosition(latitude=49.3, longitude=16.8, altitude=420))
        with self.app.test_client() as c:
            c.post('/v2/management/stop', json=self.stop_A)
            c.post('/v2/management/stop', json=self.stop_B)
            c.post('/v2/management/stop', json=self.stop_C)
            c.post('/v2/management/stop', json=self.stop_D)

    def test_defining_route_list_of_stops(self):
        route = Route(id=5, name="test_route", stop_ids=[self.stop_A.id, self.stop_B.id])
        with self.app.test_client() as c:
            response = c.post('/v2/management/route', json=route)
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/v2/management/route/{route.id}')
            self.assertEqual(response.status_code, 200)
            print(response.json)


    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == '__main__':
    unittest.main() # pragma: no coverages