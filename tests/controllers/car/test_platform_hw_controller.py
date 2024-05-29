import unittest
import sys

sys.path.append(".")

import fleet_management_api.app as _app
from fleet_management_api.database.connection import set_connection_source_test
from fleet_management_api.models import PlatformHW, Car, MobilePhone
from tests.utils.setup_utils import create_route, create_stops


class Test_Creating_Platform_HW(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_creating_platform_hw_id(self):
        platform_hw = PlatformHW(id=5, name="test_platform")
        with self.app.test_client() as c:
            response = c.post("/v2/management/platformhw", json=[platform_hw])
            self.assertEqual(response.status_code, 200)

    def test_creating_platform_hw_with_already_taken_name_returns_code_400(self):
        platform_hw_1 = PlatformHW(name="test_platform")
        platform_hw_2 = PlatformHW(name="test_platform")
        with self.app.test_client() as c:
            response = c.post("/v2/management/platformhw", json=[platform_hw_1])
            self.assertEqual(response.status_code, 200)
            response = c.post("/v2/management/platformhw", json=[platform_hw_2])
            self.assertEqual(response.status_code, 400)


class Test_Adding_Platform_HW_Using_Example_From_Spec(unittest.TestCase):
    def test_adding_state_using_example_from_spec(self):
        set_connection_source_test()
        self.app = _app.get_test_app().app
        with self.app.test_client() as c:
            example = c.get("/v2/management/openapi.json").json["components"][
                "schemas"
            ]["PlatformHW"]["example"]
            response = c.post("/v2/management/platformhw", json=[example])
            self.assertEqual(response.status_code, 200)


class Test_Retrieving_Platform_HW(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_retrieving_existing_platform_hws(self):
        platform_hw_1 = PlatformHW(name="test_platform_1")
        platform_hw_2 = PlatformHW(name="test_platform_2")
        with self.app.test_client() as c:
            response = c.post("/v2/management/platformhw", json=[platform_hw_1, platform_hw_2])
            response = c.get("/v2/management/platformhw")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)

    def test_retrieving_platform_hws_when_no_hw_exists_yields_empty_list(self):
        # no platform hw id has been sent to the database
        with self.app.test_client() as c:
            response = c.get("/v2/management/platformhw")
            self.assertEqual(response.status_code, 200)
            self.assertListEqual(response.json, [])


class Test_Getting_Single_Platform_HW(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app().app

    def test_getting_single_existing_platform_hw(self):
        platform_hw_1 = PlatformHW(name="test_platform_y")
        platform_hw_2 = PlatformHW(name="test_platform_z")
        with self.app.test_client() as c:
            c.post("/v2/management/platformhw", json=[platform_hw_1, platform_hw_2])

            response = c.get("/v2/management/platformhw/1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["id"], 1)

            response = c.get("/v2/management/platformhw/2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["id"], 2)

    def test_retrieving_nonexistent_platform_hw_yields_code_404(self):
        nonexistent_platform_hw = 156155
        with self.app.test_client() as c:
            response = c.get(f"/v2/management/platformhw/{nonexistent_platform_hw}")
            self.assertEqual(response.status_code, 404)


class Test_Deleting_Platform_HW(unittest.TestCase):
    def setUp(self) -> None:
        set_connection_source_test()
        self.app = _app.get_test_app()
        create_stops(self.app, 7)
        create_route(self.app, stop_ids=(2, 4, 6))

    def test_deleting_an_existing_platform_hw(self):
        platform_hw = PlatformHW(name="test_platform")
        with self.app.app.test_client() as c:
            c.post("/v2/management/platformhw", json=[platform_hw])
            response = c.delete("/v2/management/platformhw/1")
            self.assertEqual(response.status_code, 200)

            response = c.get("/v2/management/platformhw")
            self.assertEqual(response.json, [])

    def test_deleting_a_nonexistent_platform_hw_yields_code_404(self):
        nonexistent_platform_hw = 156155
        with self.app.app.test_client() as c:
            response = c.delete(f"/v2/management/platformhw/{nonexistent_platform_hw}")
            self.assertEqual(response.status_code, 404)

    def test_platform_hw_cannot_be_deleted_if_it_is_used_by_some_car(self):
        platform_hw = PlatformHW(name="test_platform")
        car = Car(
            platform_hw_id=1,
            name="test_car",
            car_admin_phone=MobilePhone(phone="123456789"),
            default_route_id=1,
        )
        with self.app.app.test_client() as c:
            c.post("/v2/management/platformhw", json=[platform_hw])
            response = c.post("/v2/management/car", json=[car])
            self.assertEqual(response.status_code, 200)

            response = c.delete("/v2/management/platformhw/1")
            self.assertEqual(response.status_code, 400)
            response = c.get("/v2/management/platformhw")
            self.assertEqual(len(response.json), 1)

            c.delete("/v2/management/car/1")
            response = c.delete("/v2/management/platformhw/1")
            self.assertEqual(response.status_code, 200)
            response = c.get("/v2/management/platformhw")
            self.assertEqual(len(response.json), 0)


if __name__ == "__main__":
    unittest.main(buffer=True)  # pragma: no coverages
