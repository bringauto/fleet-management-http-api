import unittest
import sys

sys.path.append(".")

import fleet_management_api.database.connection as _connection
import fleet_management_api.app as _app
from fleet_management_api.models import Car, CarState, MobilePhone, GNSSPosition
from tests.utils.setup_utils import create_platform_hws


POSITION = GNSSPosition(latitude=48.8606111, longitude=2.337644, altitude=50)


class Test_Car_Is_Returned_With_Its_Last_State(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        self.app = _app.get_test_app()
        create_platform_hws(self.app, 2)
        self.car_1 = Car(
            platform_hw_id=1, name="car1", car_admin_phone=MobilePhone(phone="123456789")
        )
        self.car_2 = Car(
            platform_hw_id=2, name="car2", car_admin_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client() as c:
            response = c.post("/v2/management/car", json=[self.car_1, self.car_2])
            assert response.json is not None
            self.car_1 = Car.from_dict(response.json[0])
            self.car_2 = Car.from_dict(response.json[1])

    def test_car_is_returned_with_its_last_state(self):
        state_1 = CarState(status="idle", car_id=self.car_1.id)
        state_2 = CarState(status="driving", car_id=self.car_1.id)
        with self.app.app.test_client() as c:
            c.post("/v2/management/carstate", json=[state_1])
            c.post("/v2/management/carstate", json=[state_2])

        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/car/{self.car_1.id}")
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.json["lastState"]["status"], state_2.status)

    def test_cars_are_returned_with_their_last_states(self):
        state_1 = CarState(status="idle", car_id=self.car_1.id)
        state_2 = CarState(status="driving", car_id=self.car_1.id)
        state_3 = CarState(status="idle", car_id=self.car_2.id)
        state_4 = CarState(status="in_stop", car_id=self.car_2.id)
        with self.app.app.test_client() as c:
            c.post("/v2/management/carstate", json=[state_1, state_2, state_3, state_4])

        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/car")
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["lastState"]["status"], state_2.status)
            self.assertEqual(response.json[1]["lastState"]["status"], state_4.status)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
