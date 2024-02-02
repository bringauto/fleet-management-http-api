import unittest
import sys
sys.path.append('.')

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access

from tests.database.models import ParentDBModel as _ParentDBModel
from tests.database.models import ChildDBModel as _ChildDBModel
from tests.database.models import initialize_test_tables as _initialize_test_tables


class Test_Parent_Child_Models(unittest.TestCase):

    def setUp(self) -> None:
        _connection.set_connection_source_test()
        _initialize_test_tables(_connection.current_connection_source())

    def test_listing_children_of_a_parent(self):
        parent = _ParentDBModel(id=1, name="parent")
        child_A = _ChildDBModel(id=1, name="child_A", parent_id=1)
        child_B = _ChildDBModel(id=2, name="child_B", parent_id=1)
        _db_access.add(_ParentDBModel, parent)

        _db_access.add(_ChildDBModel, child_A, child_B)
        children = _db_access.get_children(_ParentDBModel, parent.id, "children")
        self.assertListEqual(children, [child_A, child_B])

    def test_deleting_parent_deleted_children(self):
        parent = _ParentDBModel(id=1, name="parent")
        child_A = _ChildDBModel(id=1, name="child_A", parent_id=1)
        child_B = _ChildDBModel(id=2, name="child_B", parent_id=1)
        other_child = _ChildDBModel(id=3, name="child_C", parent_id=-1)
        _db_access.add(_ParentDBModel, parent)

        _db_access.add(_ChildDBModel, child_A, child_B, other_child)
        _db_access.delete(_ParentDBModel, "id", parent.id)

        children = _db_access.get(_ChildDBModel)
        self.assertEqual(len(children), 1)
        self.assertListEqual(children, [other_child])


if __name__=="__main__":
    unittest.main() # pragma: no cover