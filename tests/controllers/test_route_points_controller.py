import unittest

import fleet_management_api.database.connection as _connection
from fleet_management_api.models import RoutePoints, Route, GNSSPosition
import fleet_management_api.app as _app


class Test_Posting_New_Route_Points(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.route = Route(id=12, name='test_route')

    def test_getting_routepoints_for_newly_defined_route_yields_empty_list(self):
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=self.route)
            response = c.get('/v2/management/routepoints/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["points"], [])

    def test_getting_routepoints_for_nonexistent_route_yields_404(self):
        with self.app.test_client() as c:
            response = c.get('/v2/management/routepoints/12')
            self.assertEqual(response.status_code, 404)

    def test_post_route_points_to_existing_route(self):
        points = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)]
        route_points = RoutePoints(route_id=12, points=points)
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=self.route)
        with self.app.test_client() as c:
            response = c.post('/v2/management/routepoints', json=route_points)
            self.assertEqual(response.status_code, 200)
            response = c.get('/v2/management/routepoints/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_updating_route_points(self):
        old_points = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0), GNSSPosition(47.0, 23.0, 400.0)]
        new_points = [GNSSPosition(50.0, 22.0, 350.0), GNSSPosition(-48.0, -22.0, 250.0)]
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=self.route)
            c.post('/v2/management/routepoints', json=RoutePoints(route_id=12, points=old_points))
            response_1 = c.get('/v2/management/routepoints/12')
            self.assertEqual(response_1.json["points"][0]["latitude"], 49)
            self.assertEqual(len(response_1.json["points"]), 3)
            c.post('/v2/management/routepoints', json=RoutePoints(route_id=12, points=new_points))
            response_2 = c.get('/v2/management/routepoints/12')
            self.assertEqual(response_2.json["points"][0]["latitude"], 50)
            self.assertEqual(len(response_2.json), 2)


if __name__ == '__main__':
    unittest.main() # pragma: no coverage