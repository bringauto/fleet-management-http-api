import unittest

import fleet_management_api.database.connection as connection
from fleet_management_api.models import Stop, GNSSPosition, MobilePhone
from fleet_management_api.app import get_app


class Test_Creating_Stop(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_connection_source()
        self.app = get_app().app

    def test_creating_stops(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_1", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=2, name="stop_2", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            response = c.post('/v1/stop', json=stop_1.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/stop', json=stop_2.to_dict())
            self.assertEqual(response.status_code, 200)

    def test_creating_stop_with_identical_id_yields_code_400(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_1", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=1, name="stop_2", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            response = c.post('/v1/stop', json=stop_1.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/stop', json=stop_2.to_dict())
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_identical_name_yields_code_400(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=2, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            response = c.post('/v1/stop', json=stop_1.to_dict())
            self.assertEqual(response.status_code, 200)
            response = c.post('/v1/stop', json=stop_2.to_dict())
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_invalid_json_yields_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/stop', json="invalid json")
            self.assertEqual(response.status_code, 400)

    def test_creating_stop_with_incomplete_data_yields_code_400(self):
        with self.app.test_client() as c:
            response = c.post('/v1/stop', json={})
            self.assertEqual(response.status_code, 400)
            response = c.post('/v1/stop', json={"id": 1, "name": "stop_1"})
            self.assertEqual(response.status_code, 400)


class Test_Retrieving_All_Stops(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_connection_source()
        self.app = get_app().app

    def test_retrieving_all_stops_without_creating_any_yields_code_200_and_empty_list(self):
        with self.app.test_client() as client:
            response = client.get('/v1/stop')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_retrieving_sent_stops(self):
        position = GNSSPosition(latitude=49,longitude=16,altitude=50)
        stop_1 = Stop(id=1, name="stop_X", position=position, notification_phone=MobilePhone(phone="123456789"))
        stop_2 = Stop(id=2, name="stop_Y", position=position, notification_phone=MobilePhone(phone="123456789"))
        with self.app.test_client() as c:
            c.post('/v1/stop', json=stop_1.to_dict())
            c.post('/v1/stop', json=stop_2.to_dict())
            response = c.get('/v1/stop')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)


if __name__ == '__main__':
    unittest.main() # pragma: no cover
