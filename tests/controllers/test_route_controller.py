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
            response = c.post('/v1/route', json=route)
            self.assertEqual(response.status_code, 200)

    def test_creating_route_with_already_taken_id_returns_code_400(self):
        route_1 = Route(id=1, name="test_route_1")
        route_2 = Route(id=1, name="test_route_2")
        with self.app.test_client() as c:
            response = c.post('/v1/route', json=route_1)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/route', json=route_2 )
            self.assertEqual(response.status_code, 400)

    def test_creating_route_with_already_taken_name_returns_code_400(self):
        route_1 = Route(id=1, name="test_route")
        route_2 = Route(id=516515, name="test_route")
        with self.app.test_client() as c:
            response = c.post('/v1/route', json=route_1)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/route', json=route_2 )
            self.assertEqual(response.status_code, 400)

    def test_creating_route_with_missing_id_or_name_returns_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/route', json={"name": "test_route"})
            self.assertEqual(response.status_code, 400)
            response = c.post('/v1/route', json={"id": 1})
            self.assertEqual(response.status_code, 400)


class Test_Adding_Route_Using_Example_From_Spec(unittest.TestCase):

    def test_adding_state_using_example_from_spec(self):
        set_test_connection_source()
        self.app = get_app().app
        with self.app.test_client() as c:
            example = c.get('/v1/openapi.json').json["components"]["schemas"]["Route"]["example"]
            response = c.post('/v1/route', json=example)
            self.assertEqual(response.status_code, 200)


class Test_Getting_All_Routes(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app

    def test_retrieving_existing_routes(self):
        route_1 = Route(id=1, name="test_route_1")
        route_2 = Route(id=2, name="test_route_2")
        with self.app.test_client() as c:
            c.post('/v1/route', json=route_1)
            c.post('/v1/route', json=route_2)

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
        self.route_1 = Route(id=78, name="test_route_1")
        self.route_2 = Route(id=142, name="test_route_2")
        with self.app.test_client() as c:
            c.post('/v1/route', json=self.route_1)
            c.post('/v1/route', json=self.route_2)

    def test_retrieving_existing_route(self):
        with self.app.test_client() as c:
            response = c.get('/v1/route/78')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], self.route_1.name)

            response = c.get('/v1/route/142')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], self.route_2.name)

    def test_retrieving_nonexistent_route_yields_code_404(self):
        with self.app.test_client() as c:
            response = c.get('/v1/route/999')
            self.assertEqual(response.status_code, 404)


class Test_Deleting_Route(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app
        self.route_1 = Route(id=78, name="test_route_1")
        with self.app.test_client() as c:
            c.post('/v1/route', json=self.route_1)

    def test_deleting_an_existing_Route(self):
        with self.app.test_client() as c:
            response = c.delete('/v1/route/78')
            self.assertEqual(response.status_code, 200)
            response = c.get('/v1/route/78')
            self.assertEqual(response.status_code, 404)

    def test_deleting_a_nonexistent_Route_yields_code_404(self):
        with self.app.test_client() as c:
            response = c.delete('/v1/route/999')
            self.assertEqual(response.status_code, 404)


class Test_Updating_Route(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()
        self.app = get_app().app
        self.route = Route(id=78, name="test_route_1")
        with self.app.test_client() as c:
            c.post('/v1/route', json=self.route)

    def test_updating_existing_route(self):
        updated_route = Route(id=78, name="better_name")
        with self.app.test_client() as c:
            response = c.put('/v1/route', json=updated_route)
            self.assertEqual(response.status_code, 200)

            response = c.get('/v1/route/78')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], "better_name")

    def test_updating_nonexistent_route_yields_code_404(self):
        updated_route = Route(id=999, name="better_name")
        with self.app.test_client() as c:
            response = c.put('/v1/route', json=updated_route)
            self.assertEqual(response.status_code, 404)

    def test_updating_existing_route_with_incomplete_data_yields_code_400(self):
        with self.app.test_client() as c:
            response = c.put('/v1/route', json={"id": 78})
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main() # pragma: no coverages