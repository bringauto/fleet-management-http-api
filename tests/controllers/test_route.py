import unittest

from fleet_management_api.app import get_app
from fleet_management_api.database.connection import set_test_connection_source
from fleet_management_api.models import Route


class Test_Creating_Route(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_creating_route(self):
        route = Route(id=5, name="test_route")
        with self.app.test_client() as c:
            response = c.post('/v1/route', json=route.to_dict())
            self.assertEqual(response.status_code, 200)

    def test_creating_route_with_already_taken_id_returns_code_400(self):
        route_1 = Route(id=1, name="test_route_1")
        route_2 = Route(id=1, name="test_route_2")
        with self.app.test_client() as c:
            response = c.post('/v1/route', json=route_1.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/route', json=route_2 .to_dict())
            self.assertEqual(response.status_code, 400)

    def test_creating_route_with_already_taken_name_returns_code_400(self):
        route_1 = Route(id=1, name="test_route")
        route_2 = Route(id=516515, name="test_route")
        with self.app.test_client() as c:
            response = c.post('/v1/route', json=route_1.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/route', json=route_2 .to_dict())
            self.assertEqual(response.status_code, 400)

    def test_creating_route_with_missing_id_or_name_returns_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/route', json={"name": "test_route"})
            self.assertEqual(response.status_code, 400)
            response = c.post('/v1/route', json={"id": 1})
            self.assertEqual(response.status_code, 400)


class Test_Retrieving_Route(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_retrieving_existing_routes(self):
        route_1 = Route(id=1, name="test_route_1")
        route_2 = Route(id=2, name="test_route_2")
        with self.app.test_client() as c:
            response = c.post('/v1/route', json=route_1.to_dict())
            response = c.post('/v1/route', json=route_2.to_dict())

            response = c.get('/v1/route')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_retrieving_routes_when_route_exists_yields_empty_list(self):
        with self.app.test_client() as c:
            response = c.get('/v1/route')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])


class Test_Getting_Single_Route(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_getting_single_existing_Route(self):
        pass

    def test_retrieving_nonexistent_Route_yields_code_404(self):
        pass


class Test_Deleting_Route(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_deleting_an_existing_Route(self):
        pass

    def test_deleting_a_nonexistent_Route_yields_code_404(self):
        pass


if __name__ == '__main__':
    unittest.main() # pragma: no coverages