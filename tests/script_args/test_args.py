import os
import unittest
import subprocess


class Test_Running_New_Admin_Script(unittest.TestCase):

    def test_adding_new_admin_yields_code_0(self):
        process = subprocess.run(
            [
                "python",
                "scripts/add_api_key.py",
                "test_admin",
                "config/config.json",
                "-t",
                "db_file.db"
            ],
            capture_output=True,
        )
        self.assertEqual(process.returncode, 0)

    def test_adding_new_admin_with_already_existing_name_yields_return_code_1(self):
        process = subprocess.run(
            [
                "python",
                "scripts/add_api_key.py",
                "Alice",
                "config/config.json",
                "-t",
                "db_file.db"
            ],
            capture_output=True,
        )
        process = subprocess.run(
            [
                "python",
                "scripts/add_api_key.py",
                "Alice",
                "config/config.json",
                "-t",
                "db_file.db"
            ],
            capture_output=True,
        )
        self.assertEqual(process.returncode, 1)

    def tearDown(self) -> None:
        if os.path.exists("db_file.db"):
            os.remove("db_file.db")


if __name__ == "__main__":
    unittest.main() # pragma: no cover