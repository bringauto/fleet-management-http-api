import os
import sys
sys.path.append('.')
import unittest

from fleet_management_api.models import Car, PlatformHwId, Order
import fleet_management_api.app as _app
from fleet_management_api.database.connection import set_connection_source_test


class Test_Creating_And_Getting_Cars(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test()

    def test_cars_list_is_initially_available_and_empty(self):
        app = _app.get_test_app()
        with app.app.test_client() as c:
            response = c.get('/v2/management/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_creating_and_retrieving_a_car(self):
        car = Car(id=1, name="Test Car", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            response = c.post('/v2/management/car', json=car, content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response = c.get('/v2/management/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_creating_and_retrieving_two_cars(self):
        car_1 = Car(id=1, name="Test Car 1", platform_hw_id=5)
        car_2 = Car(id=2, name="Test Car 2", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            c.post('/v2/management/car', json=car_1, content_type='application/json')
            c.post('/v2/management/car', json=car_2, content_type='application/json')
            response = c.get('/v2/management/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_creating_car_from_invalid_data_returns_400_error_code(self):
        car_dict_missing_an_id = {'name': 'Test Car', 'platformId': 5}
        app = _app.get_test_app()
        with app.app.test_client() as c:
            response = c.post('/v2/management/car', json=car_dict_missing_an_id, content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_creating_car_with_already_existing_id_returns_400_error_code(self):
        car_1 = Car(id=1, name="Test Car 1", platform_hw_id=5)
        car_2 = Car(id=1, name="Test Car 2", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            c.post('/v2/management/car', json=car_1, content_type='application/json')
            response = c.post('/v2/management/car', json=car_2, content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_creating_car_with_already_existing_name_returns_400_error_code(self):
        car_1 = Car(id=1, name="Test Car", platform_hw_id=5)
        car_2 = Car(id=2, name="Test Car", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            c.post('/v2/management/car', json=car_1, content_type='application/json')
            response = c.post('/v2/management/car', json=car_2, content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_creating_car_using_invalid_json_returns_400_error_code(self):
        app = _app.get_test_app()
        with app.app.test_client() as c:
            response = c.post('/v2/management/car', json=7)
            self.assertEqual(response.status_code, 400)


class Test_Retrieving_Single_Car(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test()

    def test_retrieving_single_existing_car(self):
        car_id = 17
        car = Car(id=car_id, name="Test Car", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            c.post('/v2/management/car', json=car, content_type='application/json')
            response = c.get(f"/v2/management/car/{car_id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['name'], car.name)

    def test_retrieving_nonexistent_car_returns_code_404(self):
        car_id = 17
        nonexistent_car_id = 25
        car = Car(id=car_id, name="Test Car", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            c.post('/v2/management/car', json=car, content_type='application/json')
            response = c.get(f"/v2/management/car/{nonexistent_car_id }")
            self.assertEqual(response.status_code, 404)


class Test_Creating_Car_Using_Example_From_Specification(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test()

    def test_posting_and_getting_car_from_example_in_specification(self):
        app = _app.get_test_app()
        with app.app.test_client() as c:
            example = c.get('/v2/management/openapi.json').json["components"]["schemas"]["Car"]["example"]
            c.post('/v2/management/car', json=example, content_type='application/json')
            response = c.get(f"/v2/management/car/{example['id']}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['name'], example['name'])


class Test_Logging_Car_Creation(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test()

    def test_succesfull_creation_of_a_car_is_logged_as_info(self):
        with self.assertLogs('werkzeug', level='INFO') as logs:
            car = Car(id=1, name="Test Car", platform_hw_id=5)
            app = _app.get_test_app()
            with app.app.test_client() as c:
                c.post('/v2/management/car', json=car, content_type='application/json')
                self.assertEqual(len(logs.output), 1)
                self.assertIn(str(car.id), logs.output[0])

    def test_unsuccesfull_creation_of_a_car_already_present_in_database_is_logged_as_error(self):
        with self.assertLogs('werkzeug', level='ERROR') as logs:
            car = Car(id=1, name="Test Car", platform_hw_id=5)
            app = _app.get_test_app()
            with app.app.test_client() as c:
                c.post('/v2/management/car', json=car, content_type='application/json')
                c.post('/v2/management/car', json=car, content_type='application/json')
                self.assertEqual(len(logs.output), 1)


class Test_Updating_Car(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test()

    def test_add_and_succesfully_update_car(self) -> None:
        car = Car(id=1, name="Test Car", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            response = c.post('/v2/management/car', json=car, content_type='application/json')
            car.name = "Updated Test Car"
            response = c.put('/v2/management/car', json=car, content_type='application/json')
            self.assertEqual(response.status_code, 200)

            response = c.get('/v2/management/car')
            self.assertTrue(len(response.json) == 1) # type: ignore
            self.assertEqual(response.json[0]['name'], "Updated Test Car") # type: ignore

    def test_updating_nonexistent_car_yields_404_error(self) -> None:
        car = Car(id=1, name="Test Car", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            response = c.put('/v2/management/car', json=car, content_type='application/json')
            self.assertEqual(response.status_code, 404)

    def test_passing_other_object_when_updating_car_yields_400_error(self) -> None:
        car = Car(id=1, name="Test Car", platform_hw_id=5)
        app = _app.get_test_app()
        with app.app.test_client() as c:
            c.post('/v2/management/car', json=car)
            response = c.put('/v2/management/car', json={'id': 1}, content_type='application/json')
            self.assertEqual(response.status_code, 400)


class Test_Deleting_Car(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source_test("test_db.db")

    def test_add_and_delete_car(self) -> None:
        app = _app.get_test_app()
        platform_hw_id = PlatformHwId(id=5, name="Test Platform Hw Id")
        car = Car(id=1, name="Test Car", platform_hw_id=5)
        with app.app.test_client() as c:
            c.post('/v2/management/platformhwid', json=platform_hw_id)
            c.post('/v2/management/car', json=car)
            response = c.delete('/v2/management/car/1')
            self.assertEqual(response.status_code, 200)
            response = c.get('/v2/management/car')
            self.assertEqual(response.json, [])

    def test_deleting_nonexistent_car_yields_404_error(self) -> None:
        car_id = 17
        app = _app.get_test_app()
        with app.app.test_client() as c:
            response = c.delete(f'/v2/management/car/{car_id}')
            self.assertEqual(response.status_code, 404)

    def test_car_with_assigned_order_cannot_be_deleted(self):
        order = Order(
            id=1,
            user_id=789,
            car_id=1,
            target_stop_id=7,
            stop_route_id=8,
        )
        app = _app.get_test_app()
        car = Car(id=1, name="Test Car", platform_hw_id=5)
        with app.app.test_client() as c:
            c.post('/v2/management/car', json=car)
            c.post('/v2/management/order', json=order)
            response = c.delete('/v2/management/car/1')
            self.assertEqual(response.status_code, 400)

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__=="__main__": # pragma: no cover
    unittest.main(buffer=True)
