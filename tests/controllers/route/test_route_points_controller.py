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
        route_points = RoutePoints(id=4, route_id=12, points=points)
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=self.route)
        with self.app.test_client() as c:
            response = c.post('/v2/management/routepoints', json=route_points)
            self.assertEqual(response.status_code, 200)
            response = c.get('/v2/management/routepoints/12')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["id"], 4)
            self.assertEqual(response.json["routeId"], 12)
            self.assertEqual(len(response.json["points"]), 2)


class Updating_Route_Points(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.route = Route(id=12, name='test_route')

    def test_updating_route_points(self):
        old_points = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0), GNSSPosition(47.0, 23.0, 400.0)]
        new_points = [GNSSPosition(50.0, 22.0, 350.0), GNSSPosition(-48.0, -22.0, 250.0)]
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=self.route)

            c.post('/v2/management/routepoints', json=RoutePoints(id=3, route_id=12, points=old_points))
            response_1 = c.get('/v2/management/routepoints/12')
            self.assertEqual(response_1.json["id"], 3)
            self.assertEqual(len(response_1.json["points"]), 3)
            self.assertEqual(response_1.json["points"][0]["latitude"], 49)

            c.post('/v2/management/routepoints', json=RoutePoints(id=6, route_id=12, points=new_points))
            response_2 = c.get('/v2/management/routepoints/12')
            self.assertEqual(response_2.json["id"], 6)
            self.assertEqual(len(response_2.json["points"]), 2)
            self.assertEqual(response_2.json["points"][0]["latitude"], 50)

    def test_updating_route_points_with_keeping_their_id_is_possible(self):
        old_points = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0), GNSSPosition(47.0, 23.0, 400.0)]
        new_points = [GNSSPosition(50.0, 22.0, 350.0), GNSSPosition(-48.0, -22.0, 250.0)]
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=self.route)

            c.post('/v2/management/routepoints', json=RoutePoints(id=3, route_id=12, points=old_points))
            response_2 = c.get('/v2/management/routepoints/12')
            self.assertEqual(len(response_2.json["points"]), 3)

            c.post('/v2/management/routepoints', json=RoutePoints(id=3, route_id=12, points=new_points))
            response_2 = c.get('/v2/management/routepoints/12')
            self.assertEqual(len(response_2.json["points"]), 2)

    def test_updating_route_points_for_nonexistent_route_yields_404(self):
        points = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)]
        route_points = RoutePoints(id=3, route_id=12, points=points)
        with self.app.test_client() as c:
            response = c.post('/v2/management/routepoints', json=route_points)
            self.assertEqual(response.status_code, 404)


class Test_Route_Removal(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_route_points_are_not_accessible_after_route_is_removed(self):
        route = Route(id=12, name='test_route')
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=route)
            response = c.delete('/v2/management/route/12')
            self.assertEqual(response.status_code, 200)
            response = c.get('/v2/management/routepoints/12')
            self.assertEqual(response.status_code, 404)

    def test_route_points_can_be_recreated_under_the_same_id_after_removal_of_the_original_one(self):
        old_route = Route(id=12, name='old_test_route')
        new_route = Route(id=12, name='new_test_route')
        new_route_points = RoutePoints(id=12, route_id=12, points=[GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)])
        with self.app.test_client() as c:
            c.post('/v2/management/route', json=old_route)
            c.delete('/v2/management/route/12')
            response = c.post('/v2/management/route', json=new_route)
            self.assertEqual(response.status_code, 200)
            response = c.get('/v2/management/routepoints/12')
            self.assertEqual(response.status_code, 200)
            response = c.post('/v2/management/routepoints', json=new_route_points)
            self.assertEqual(response.status_code, 200)
            response = c.get('/v2/management/routepoints/12')
            self.assertEqual(response.json["points"][0]["latitude"], 49)


if __name__ == '__main__':
    unittest.main(buffer=True) # pragma: no coverage