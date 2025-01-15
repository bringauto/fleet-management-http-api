import unittest

import fleet_management_api.database.db_models as _db_models


class Test_Setting_Maximum_Number_Of_Car_And_Order_States(unittest.TestCase):
    def test_maximum_number_of_car_states_must_be_positive_integer(self):
        _db_models.CarStateDB.set_max_n_of_stored_states(1)
        self.assertEqual(_db_models.CarStateDB.max_n_of_stored_states(), 1)
        _db_models.CarStateDB.set_max_n_of_stored_states(8)
        self.assertEqual(_db_models.CarStateDB.max_n_of_stored_states(), 8)
        _db_models.CarStateDB.set_max_n_of_stored_states(0)
        self.assertEqual(_db_models.CarStateDB.max_n_of_stored_states(), 8)
        _db_models.CarStateDB.set_max_n_of_stored_states(-1)
        self.assertEqual(_db_models.CarStateDB.max_n_of_stored_states(), 8)

    def test_maximum_number_of_order_states_must_be_positive_integer(self):
        _db_models.OrderStateDB.set_max_n_of_stored_states(1)
        self.assertEqual(_db_models.OrderStateDB.max_n_of_stored_states(), 1)
        _db_models.OrderStateDB.set_max_n_of_stored_states(8)
        self.assertEqual(_db_models.OrderStateDB.max_n_of_stored_states(), 8)
        _db_models.OrderStateDB.set_max_n_of_stored_states(0)
        self.assertEqual(_db_models.OrderStateDB.max_n_of_stored_states(), 8)
        _db_models.OrderStateDB.set_max_n_of_stored_states(-1)
        self.assertEqual(_db_models.OrderStateDB.max_n_of_stored_states(), 8)

    def test_maximum_number_of_car_action_states_must_be_positive_integer(self):
        _db_models.CarActionStateDBModel.set_max_n_of_stored_states(1)
        self.assertEqual(_db_models.CarActionStateDBModel.max_n_of_stored_states(), 1)
        _db_models.CarActionStateDBModel.set_max_n_of_stored_states(8)
        self.assertEqual(_db_models.CarActionStateDBModel.max_n_of_stored_states(), 8)
        _db_models.CarActionStateDBModel.set_max_n_of_stored_states(0)
        self.assertEqual(_db_models.CarActionStateDBModel.max_n_of_stored_states(), 8)
        _db_models.CarActionStateDBModel.set_max_n_of_stored_states(-1)
        self.assertEqual(_db_models.CarActionStateDBModel.max_n_of_stored_states(), 8)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
