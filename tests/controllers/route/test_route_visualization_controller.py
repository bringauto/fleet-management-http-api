import unittest

import fleet_management_api.database.connection as _connection
from fleet_management_api.models import RouteVisualization, Route, GNSSPosition
import fleet_management_api.app as _app


class Test_Posting_New_Route_Visualization(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.route = Route(name="test_route")

    def test_getting_route_visualization_for_newly_defined_route_yields_empty_list(self):
        with self.app.test_client() as c:
            c.post("/v2/management/route", json=[self.route])
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["points"], [])

    def test_getting_route_visualization_for_nonexistent_route_yields_404(self):
        with self.app.test_client() as c:
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.status_code, 404)

    def test_post_route_visualization_to_existing_route(self):
        points = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)]
        route_visualization = RouteVisualization(route_id=1, points=points, hexcolor="#FF0000")
        with self.app.test_client() as c:
            response = c.post("/v2/management/route", json=[self.route])
            self.assertEqual(response.status_code, 200)
        with self.app.test_client() as c:
            response = c.post("/v2/management/route-visualization", json=[route_visualization])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["id"], 1)
            self.assertEqual(response.json["routeId"], 1)
            self.assertEqual(len(response.json["points"]), 2)

    def test_post_route_visualizations_to_multiple_existing_routes(self):
        points_1 = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)]
        points_2 = [
            GNSSPosition(49.0, 21.0, 300.0),
            GNSSPosition(48.0, 22.0, 350.0),
            GNSSPosition(47.0, 23.0, 400.0),
        ]
        route_2 = Route(name="test_route_2")
        vis_1 = RouteVisualization(route_id=1, points=points_1, hexcolor="#FF0000")
        vis_2 = RouteVisualization(route_id=2, points=points_2, hexcolor="#FFEE00")
        with self.app.test_client() as c:
            response = c.post("/v2/management/route", json=[self.route, route_2])
            self.assertEqual(response.status_code, 200)
        with self.app.test_client() as c:
            response = c.post("/v2/management/route-visualization", json=[vis_1, vis_2])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["routeId"], 1)
            self.assertEqual(len(response.json["points"]), 2)
            self.assertEqual(response.json["hexcolor"], "#FF0000")
            response = c.get("/v2/management/route-visualization/2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["routeId"], 2)
            self.assertEqual(len(response.json["points"]), 3)
            self.assertEqual(response.json["hexcolor"], "#FFEE00")

    def test_post_route_visualizations_to_multiple_existing_routes_with_one_nonexistent_yields_no_update(
        self,
    ):
        points_1 = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)]
        points_2 = [GNSSPosition(49.0, 21.0, 300.0)]
        vis_1 = RouteVisualization(route_id=1, points=points_1, hexcolor="#FF0000")
        # route for the following visualization does not exist
        vis_2 = RouteVisualization(route_id=25252, points=points_2, hexcolor="#FFEE00")
        with self.app.test_client() as c:
            response = c.post("/v2/management/route", json=[self.route])
            self.assertEqual(response.status_code, 200)
        with self.app.test_client() as c:
            response = c.post("/v2/management/route-visualization", json=[vis_1, vis_2])
            self.assertEqual(response.status_code, 404)
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.status_code, 200)
            # as no update occured, the number of points is still 0 instead of 2
            self.assertEqual(len(response.json["points"]), 0)

    def test_route_visualization_accepts_only_hexadecimal_color_code(self):
        invalid_colors = ["#FF000", "#", "   ", "red"]
        with self.app.test_client() as c:
            c.post("/v2/management/route", json=[self.route])
        for color in invalid_colors:
            with self.subTest(color=color):
                visualization_json = {"points": [], "routeId": 1, "hexcolor": color}
                response = c.post("/v2/management/route-visualization", json=[visualization_json])
                print(response.json)
                self.assertEqual(response.status_code, 400)


class Updating_Route_Visualization(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app
        self.route = Route(name="test_route")

    def test_updating_route_visualization(self):
        old_points = [
            GNSSPosition(49.0, 21.0, 300.0),
            GNSSPosition(48.0, 22.0, 350.0),
            GNSSPosition(47.0, 23.0, 400.0),
        ]
        new_points = [
            GNSSPosition(50.0, 22.0, 350.0),
            GNSSPosition(-48.0, -22.0, 250.0),
        ]
        with self.app.test_client() as c:
            c.post("/v2/management/route", json=[self.route])

            c.post(
                "/v2/management/route-visualization",
                json=[RouteVisualization(route_id=1, points=old_points)],
            )
            response_1 = c.get("/v2/management/route-visualization/1")
            self.assertEqual(len(response_1.json["points"]), 3)
            self.assertEqual(response_1.json["points"][0]["latitude"], 49)

            c.post(
                "/v2/management/route-visualization",
                json=[RouteVisualization(route_id=1, points=new_points)],
            )
            response_2 = c.get("/v2/management/route-visualization/1")
            self.assertEqual(len(response_2.json["points"]), 2)
            self.assertEqual(response_2.json["points"][0]["latitude"], 50)

    def test_updating_route_visualization_with_keeping_their_id_is_possible(self):
        old_points = [
            GNSSPosition(49.0, 21.0, 300.0),
            GNSSPosition(48.0, 22.0, 350.0),
            GNSSPosition(47.0, 23.0, 400.0),
        ]
        new_points = [
            GNSSPosition(50.0, 22.0, 350.0),
            GNSSPosition(-48.0, -22.0, 250.0),
        ]
        with self.app.test_client() as c:
            c.post("/v2/management/route", json=[self.route])

            c.post(
                "/v2/management/route-visualization",
                json=[RouteVisualization(route_id=1, points=old_points)],
            )
            response_2 = c.get("/v2/management/route-visualization/1")
            self.assertEqual(len(response_2.json["points"]), 3)

            c.post(
                "/v2/management/route-visualization",
                json=[RouteVisualization(route_id=1, points=new_points)],
            )
            response_2 = c.get("/v2/management/route-visualization/1")
            self.assertEqual(len(response_2.json["points"]), 2)

    def test_updating_route_visualization_for_nonexistent_route_yields_404(self):
        points = [GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)]
        route_visualization = RouteVisualization(route_id=1, points=points)
        with self.app.test_client() as c:
            response = c.post("/v2/management/route-visualization", json=[route_visualization])
            self.assertEqual(response.status_code, 404)


class Test_Route_Removal(unittest.TestCase):
    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_route_visualization_are_not_accessible_after_route_is_removed(self):
        route = Route(name="test_route")
        with self.app.test_client() as c:
            c.post("/v2/management/route", json=[route])
            response = c.delete("/v2/management/route/1")
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.status_code, 404)

    def test_route_visualization_can_be_recreated_under_the_same_id_after_removal_of_the_original_one(
        self,
    ):
        old_route = Route(id=12, name="old_test_route")
        new_route = Route(id=12, name="new_test_route")
        new_route_visualization = RouteVisualization(
            route_id=1,
            points=[GNSSPosition(49.0, 21.0, 300.0), GNSSPosition(48.0, 22.0, 350.0)],
        )
        with self.app.test_client() as c:
            c.post("/v2/management/route", json=[old_route])
            c.delete("/v2/management/route/1")
            response = c.post("/v2/management/route", json=[new_route])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.status_code, 200)
            response = c.post("/v2/management/route-visualization", json=[new_route_visualization])
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/route-visualization/1")
            self.assertEqual(response.json["points"][0]["latitude"], 49)


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no coverage
