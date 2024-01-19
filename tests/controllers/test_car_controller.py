import sys
sys.path.append('.')
import unittest

from fleet_management_api.models import Car
from fleet_management_api.app import get_app
from fleet_management_api.database.connection import set_test_connection_source


class Test_Cars(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()

    def test_cars_list_is_initially_available_and_empty(self):
        app = get_app()
        with app.app.test_client() as c:
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_creating_and_retrieving_a_car(self):
        car = Car(id=1, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            response = c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_creating_and_retrieving_two_cars(self):
        car_1 = Car(id=1, name="Test Car 1", platform_id=5)
        car_2 = Car(id=2, name="Test Car 2", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car_1.to_dict(), content_type='application/json')
            c.post('/v1/car', json = car_2.to_dict(), content_type='application/json')
            response = c.get('/v1/car')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_creating_car_from_invalid_data_returns_400_error_code(self):
        car_dict_missing_an_id = {'name': 'Test Car', 'platform_id': 5}
        app = get_app()
        with app.app.test_client() as c:
            response = c.post('/v1/car', json = car_dict_missing_an_id, content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_creating_car_with_already_existing_id_returns_400_error_code(self):
        car_1 = Car(id=1, name="Test Car 1", platform_id=5)
        car_2 = Car(id=1, name="Test Car 2", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car_1.to_dict(), content_type='application/json')
            response = c.post('/v1/car', json = car_2.to_dict(), content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_creating_car_with_already_existing_name_returns_400_error_code(self):
        car_1 = Car(id=1, name="Test Car", platform_id=5)
        car_2 = Car(id=2, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car_1.to_dict(), content_type='application/json')
            response = c.post('/v1/car', json = car_2.to_dict(), content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_creating_car_using_invalid_json_returns_400_error_code(self):
        app = get_app()
        with app.app.test_client() as c:
            response = c.post('/v1/car', json=7)
            self.assertEqual(response.status_code, 400)


class Test_Retrieving_Single_Car(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()

    def test_retrieving_single_existing_car(self):
        car_id = 17
        car = Car(id=car_id, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            response = c.get(f"/v1/car/{car_id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['name'], car.name)

    def test_retrieving_nonexistent_car_returns_code_404(self):
        car_id = 17
        nonexistent_car_id = 25
        car = Car(id=car_id, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            response = c.get(f"/v1/car/{nonexistent_car_id }")
            self.assertEqual(response.status_code, 404)


class Test_Logging_Car_Creation(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()

    def test_succesfull_creation_of_a_car_is_logged_as_info(self):
        with self.assertLogs('werkzeug', level='INFO') as logs:
            car = Car(id=1, name="Test Car", platform_id=5)
            app = get_app()
            with app.app.test_client() as c:
                c.post('/v1/car', json = car.to_dict(), content_type='application/json')
                self.assertEqual(len(logs.output), 1)
                self.assertIn(str(car.id), logs.output[0])

    def test_unsuccesfull_creation_of_a_car_already_present_in_database_is_logged_as_error(self):
        with self.assertLogs('werkzeug', level='ERROR') as logs:
            car = Car(id=1, name="Test Car", platform_id=5)
            app = get_app()
            with app.app.test_client() as c:
                c.post('/v1/car', json = car.to_dict(), content_type='application/json')
                c.post('/v1/car', json = car.to_dict(), content_type='application/json')
                self.assertEqual(len(logs.output), 1)


class Test_Updating_Car(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()

    def test_add_and_succesfully_update_car(self) -> None:
        car = Car(id=1, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            car.name = "Updated Test Car"
            response = c.put('/v1/car', json = car.to_dict(), content_type='application/json')
            self.assertEqual(response.status_code, 200)

            response = c.get('/v1/car')
            self.assertEqual(response.json[0]['name'], "Updated Test Car")

    def test_updating_nonexistent_car_yields_404_error(self) -> None:
        car = Car(id=1, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            response = c.put('/v1/car', json = car.to_dict(), content_type='application/json')
            self.assertEqual(response.status_code, 404)

    def test_passing_other_object_when_updating_car_yields_400_error(self) -> None:
        car = Car(id=1, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            response = c.put('/v1/car', json = {'id': 1}, content_type='application/json')
            self.assertEqual(response.status_code, 400)


class Test_Deleting_Car(unittest.TestCase):

    def setUp(self) -> None:
        set_test_connection_source()

    def test_add_and_delete_car(self) -> None:
        car_id = 4
        car = Car(id=car_id, name="Test Car", platform_id=5)
        app = get_app()
        with app.app.test_client() as c:
            c.post('/v1/car', json = car.to_dict(), content_type='application/json')
            response = c.delete(f'/v1/car/{car_id}')
            self.assertEqual(response.status_code, 200)
            response = c.get('/v1/car')
            self.assertEqual(response.json, [])

    def test_deleting_nonexistent_car_yields_404_error(self) -> None:
        car_id = 17
        app = get_app()
        with app.app.test_client() as c:
            response = c.delete(f'/v1/car/{car_id}')
            self.assertEqual(response.status_code, 404)



if __name__=="__main__":
    unittest.main()
