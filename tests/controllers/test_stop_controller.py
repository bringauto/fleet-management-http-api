import unittest

import fleet_management_api.database.connection as _connection
from fleet_management_api.models import Stop, GNSSPosition, MobilePhone
import fleet_management_api.app as _app


class Test_Creating_Stop(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_creating_stops(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_1", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=2, name="stop_2", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            response = c.post('/v2/management/stop', json=stop_1)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v2/management/stop', json=stop_2)
            self.assertEqual(response.status_code, 200)

    def test_creating_stop_with_identical_id_yields_code_400(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_1", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=1, name="stop_2", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            response = c.post('/v2/management/stop', json=stop_1)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v2/management/stop', json=stop_2)
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_identical_name_yields_code_400(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=2, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            response = c.post('/v2/management/stop', json=stop_1)
            self.assertEqual(response.status_code, 200)
            response = c.post('/v2/management/stop', json=stop_2)
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_invalid_json_yields_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v2/management/stop', json="invalid json")
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_incomplete_data_yields_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v2/management/stop', json={})
            self.assertEqual(response.status_code, 400)
            response = c.post('/v2/management/stop', json={"id": 1, "name": "stop_1"})
            self.assertEqual(response.status_code, 400)


class Test_Adding_Stop_Using_Example_From_Spec(unittest.TestCase):

    def test_adding_stop_using_example_from_spec(self):
        _connection.set_connection_source_test()
        app = _app.get_test_app().app
        with app.test_client() as c:
            example = c.get('/v2/management/openapi.json').json["components"]["schemas"]["Stop"]["example"]
            response = c.post('/v2/management/stop', json=example)
            self.assertEqual(response.status_code, 200)


class Test_Retrieving_All_Stops(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_retrieving_all_stops_without_creating_any_yields_code_200_and_empty_list(self):
        with self.app.test_client() as client:
            response = client.get('/v2/management/stop')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_retrieving_sent_stops(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=2, name="stop_Y", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            c.post('/v2/management/stop', json=stop_1)
            c.post('/v2/management/stop', json=stop_2)
            response = c.get('/v2/management/stop')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


class Test_Retrieving_Single_Stop(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_retrieving_single_existing_stop(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1234, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=4321, name="stop_Y", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            c.post('/v2/management/stop', json=stop_1)
            c.post('/v2/management/stop', json=stop_2)

            response = c.get('/v2/management/stop/1234')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], stop_1.name)

            response = c.get('/v2/management/stop/4321')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["name"], stop_2.name)

    def test_retrieving_single_non_existing_stop_yields_code_404(self):
        with self.app.test_client() as c:
            response = c.get('/v2/management/stop/1234')
            self.assertEqual(response.status_code, 404)


class Test_Deleting_Stop(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_deleting_single_existing_stop(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop = Stop(id=1234, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            c.post('/v2/management/stop', json=stop)
            response = c.get('/v2/management/stop')

            self.assertEqual(len(response.json), 1)

            response = c.delete('/v2/management/stop/1234')
            self.assertEqual(response.status_code, 200)

            response = c.get('/v2/management/stop')
            self.assertEqual(len(response.json), 0)

    def test_deleting_single_non_existing_stop_yields_code_404(self):
        with self.app.test_client() as c:
            response = c.delete('/v2/management/stop/1234')
            self.assertEqual(response.status_code, 404)


class Test_Updating_Stop(unittest.TestCase):

    def setUp(self):
        _connection.set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_updating_single_existing_stop(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop = Stop(id=1234, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            c.post('/v2/management/stop', json=stop)
            stop.name = "stop_Y"
            response = c.put('/v2/management/stop', json=stop)
            self.assertEqual(response.status_code, 200)

            response = c.get('/v2/management/stop/1234')
            self.assertEqual(response.json["name"], "stop_Y")

    def test_updating_nonexisting_stop_yields_code_404(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop = Stop(id=1234, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))

        with self.app.test_client() as c:
            response = c.put('/v2/management/stop', json=stop)
            self.assertEqual(response.status_code, 404)

    def test_updating_stop_with_incomplete_data_yields_code_400(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop = Stop(id=1234, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            c.post('/v2/management/stop', json=stop)

            response = c.put('/v2/management/stop', json={"id": 1234, "name": "stop_Y"})
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main() # pragma: no cover
