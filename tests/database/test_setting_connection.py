import unittest

import fleet_management_api.database.connection as connection


class Test_Creating_Database_URL(unittest.TestCase):

    def test_production_database_url_with_specified_username_and_password(self):
        url = connection.db_url_production("localhost", "test_user", "test_password", "test_db")
        self.assertEqual(url, "postgresql:psycopg://test_user:test_password@localhost/test_db")

    def test_production_database_url_without_username_and_password(self):
        url = connection.db_url_production("localhost", db_name="test_db")
        self.assertEqual(url, "postgresql:psycopg://localhost/test_db")

    def test_test_database_url(self):
        url = connection.db_url_test()
        self.assertEqual(url, "sqlite:///:memory:")

    def test_test_database_url_with_specified_file_location(self):
        url = connection.db_url_test("test_db_file")
        self.assertEqual(url, "sqlite:///test_db_file")


if __name__=="__main__":
    unittest.main() # pragma: no cover