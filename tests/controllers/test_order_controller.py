import unittest

import fleet_management_api.database.connection as connection
from fleet_management_api.models import Order


class Test_Getting_Order(unittest.TestCase):

    def setUp(self) -> None:
        connection.set_connection_source()

    def test_getting_order(self):
        order = Order(id=1, user_id=789, car_id=12, target_stop_id=7)



if __name__ == '__main__':
    unittest.main() # pragma: no coverage