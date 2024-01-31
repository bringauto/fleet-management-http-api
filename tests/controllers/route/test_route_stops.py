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
        route = Route(id=5, name="test_route", stop_ids=[self.stop_A.id, self.stop_C.id])
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=route)
            response = c.get(f'/v2/management/route/{route.id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["stopIds"], [self.stop_A.id, self.stop_C.id])

    def test_updating_list_of_stops(self):
        route = Route(id=5, name="test_route", stop_ids=[self.stop_A.id, self.stop_C.id])
        with self.app.test_client() as c:
            response=c.post('/v2/management/route', json=route)
            self.assertEqual(response.status_code, 200)
            route.stop_ids.append(self.stop_B.id)
            c.put('/v2/management/route', json=route)
            response = c.get(f'/v2/management/route/{route.id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["stopIds"], [self.stop_A.id, self.stop_C.id, self.stop_B.id])

    def test_creating_list_of_routes_with_nonexistent_stop_yields_code_404(self):
        nonexistent_stop_id = 123
        route = Route(id=5, name="test_route", stop_ids=[self.stop_A.id, nonexistent_stop_id])
        with self.app.test_client() as c:
            response = c.post('/v2/management/route', json=route)
            self.assertEqual(response.status_code, 404)

    def test_route_is_not_created_if_any_of_its_stops_does_not_exist(self):
        nonexistent_stop_id = 123
        route = Route(id=5, name="test_route", stop_ids=[self.stop_A.id, nonexistent_stop_id])
        with self.app.test_client() as c:
            response = c.post('/v2/management/route', json=route)
            self.assertEqual(response.status_code, 404)

            response = c.get(f'/v2/management/route')
            self.assertEqual(response.json, [])

    def test_updating_list_of_stops_with_nonexistent_stop_yields_code_404(self):
        nonexistent_stop_id = 123
        route = Route(id=5, name="test_route", stop_ids=[self.stop_A.id, self.stop_C.id])
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=route)
            route.stop_ids.append(nonexistent_stop_id)
            response = c.put('/v2/management/route', json=route)
            self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Deleting_Stops_Referenced_By_Route(unittest.TestCase):

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

    def test_deleting_stop_no_referenced_by_any_route_is_allowed(self):
        with self.app.test_client() as c:
            response = c.delete(f'/v2/management/stop/{self.stop_A.id}')
            self.assertEqual(response.status_code, 200)
            response = c.get(f'/v2/management/stop')
            self.assertEqual(len(response.json), 3)

    def test_attempting_to_delete_stop_referenced_by_route_yields_code_400_and_does_not_delete_the_stop(self):
        route_1 = Route(id=5, name="test_route_1", stop_ids=[self.stop_A.id, self.stop_C.id])
        route_2 = Route(id=6, name="test_route_2", stop_ids=[self.stop_B.id, self.stop_C.id])
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=route_1)
            c.post('/v2/management/route', json=route_2)
            response = c.delete(f'/v2/management/stop/{self.stop_A.id}')
            self.assertEqual(response.status_code, 400)
            response = c.delete(f'/v2/management/stop/{self.stop_B.id}')
            self.assertEqual(response.status_code, 400)
            response = c.get(f'/v2/management/stop')
            self.assertEqual(len(response.json), 4)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == '__main__':
    unittest.main() # pragma: no coverages