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
        self.car = Car(
            platform_hw_id=1,
            name="car1",
            car_admin_phone=MobilePhone(phone="123456789")
        )
        with self.app.app.test_client() as c:
            self.car = Car.from_dict(c.post("/v2/management/car", json=self.car).json)

        state_1 = CarState(status="idle", car_id=self.car.id, position=POSITION)
        state_2 = CarState(status="charging", car_id=self.car.id, position=POSITION)

    def test_car_is_returned_with_its_last_state(self):
        with self.app.app.test_client() as c:
            response = c.get(f"/v2/management/car/{self.car.id}")
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.json["last_state"]["status"], "out_of_order")


if __name__=='__main__':  # pragma: no cover
    unittest.main()