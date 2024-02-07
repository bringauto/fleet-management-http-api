import unittest
import sys
sys.path.append('.')

import fleet_management_api.database.connection as _connection
import fleet_management_api.database.db_access as _db_access
import tests.database.models as models


class Test_Many_To_Many_Relationship(unittest.TestCase):

    def setUp(self):
        _connection.set_connection_source_test()
        models.initialize_test_tables(_connection.current_connection_source())

    def test_creating_independent_child_and_parent(self):
        parent = models.ParentDBModel(id=2, name="parent")
        child = models.ChildDBModel(id=5, name="child")
        _db_access.add(models.ParentDBModel, parent)
        _db_access.add(models.ChildDBModel, child)

        self.assertEqual([parent], _db_access.get_by_id(models.ParentDBModel, parent.id))
        self.assertEqual([child], _db_access.get_by_id(models.ChildDBModel, child.id))

    def test_assigning_existing_child_to_a_parent(self):
        parent_A = models.ParentDBModel(id=2, name="parent_A")
        parent_B = models.ParentDBModel(id=3, name="parent_B")

        child_a = models.ChildDBModel(id=5, name="child_a")
        child_b = models.ChildDBModel(id=6, name="child_b")
        child_c = models.ChildDBModel(id=7, name="child_c")

        _db_access.add(models.ParentDBModel, parent_A, parent_B)
        _db_access.add(models.ChildDBModel, child_a, child_b, child_c)

        relationship_1 = models.FamilyRelationship(id=1, parent_id=parent_A.id, child_id=child_a.id)
        relationship_2 = models.FamilyRelationship(id=2, parent_id=parent_A.id, child_id=child_b.id)
        relationship_3 = models.FamilyRelationship(id=3, parent_id=parent_B.id, child_id=child_b.id)

        _db_access.add(models.FamilyRelationship,  relationship_1, relationship_2, relationship_3)
        result = _db_access.get(models.FamilyRelationship, criteria={"parent_id": lambda x: x==parent_A.id})
        self.assertEqual(result, [relationship_1, relationship_2])



if __name__=="__main__":
    unittest.main()
