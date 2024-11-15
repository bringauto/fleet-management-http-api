import unittest

import fleet_management_api.database.db_access as _db_access
import tests.database.models as models
import tests._utils.api_test as api_test
from tests._utils.constants import TEST_TENANT


class Test_Object_Existence(api_test.TestCase):

    def test_object_exists_after_it_is_added_to_the_database(self):
        test_obj = models.TestBase(test_str="test_string", test_int=5)
        self.assertFalse(
            _db_access.exists(
                tenant=TEST_TENANT,
                base=models.TestBase,
                criteria={"id": lambda x: x == test_obj.id},
            )
        )
        _db_access.add(TEST_TENANT, test_obj)
        self.assertTrue(
            _db_access.exists(
                tenant=TEST_TENANT,
                base=models.TestBase,
                criteria={"id": lambda x: x == test_obj.id},
            )
        )

    def test_object_does_not_exist_after_it_is_deleted_from_the_database(self):
        test_obj = models.TestBase(test_str="test_string", test_int=5)
        _db_access.add(TEST_TENANT, test_obj)

        self.assertTrue(
            _db_access.exists(
                tenant=TEST_TENANT,
                base=models.TestBase,
                criteria={"id": lambda x: x == test_obj.id},
            )
        )
        _db_access.delete(tenant=TEST_TENANT, base=models.TestBase, id_=test_obj.id)
        self.assertFalse(
            _db_access.exists(
                tenant=TEST_TENANT,
                base=models.TestBase,
                criteria={"id": lambda x: x == test_obj.id},
            )
        )

    def test_object_still_exists_after_being_updated(self):
        test_obj = models.TestBase(test_str="test_string", test_int=5)
        _db_access.add(TEST_TENANT, test_obj)

        self.assertTrue(
            _db_access.exists(
                tenant=TEST_TENANT,
                base=models.TestBase,
                criteria={"id": lambda x: x == test_obj.id},
            )
        )
        test_obj.test_str = "new_string"
        _db_access.update(TEST_TENANT, test_obj)
        self.assertTrue(
            _db_access.exists(
                tenant=TEST_TENANT,
                base=models.TestBase,
                criteria={"id": lambda x: x == test_obj.id},
            )
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
