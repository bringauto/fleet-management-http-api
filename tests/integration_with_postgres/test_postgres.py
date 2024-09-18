import unittest
import subprocess


class Test_Database_Cleanup(unittest.TestCase):

    def test_database_cleanup(self):
        # This test will fail if the database is not cleaned up
        subprocess.run(["docker", "compose", "down"])
        subprocess.run(["docker", "compose", "up", "-d"])

        subprocess.run(["docker", "compose", "stop", "postgresql-database"])
        subprocess.run(["docker", "compose", "rm", "postgresql-database", "-f"])

        subprocess.run(["docker", "compose", "up", "postgresql-database", "-d"])

        subprocess.run(["curl", "-X", "GET", "http://localhost:8080/v2/management/car?api_key="])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
