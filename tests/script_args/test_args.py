import os
import sys
import unittest
import subprocess


# Get the project root directory (parent of tests directory)
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(TEST_DIR))
DB_FILE = os.path.join(PROJECT_ROOT, "db_file.db")

RUN_CONTENT = [
    sys.executable,
    os.path.join(PROJECT_ROOT, "scripts/add_api_key.py"),
    "Alice",
    os.path.join(TEST_DIR, "test_config.json"),
    "-t",
    DB_FILE,
]


class Test_Running_New_API_Key_Script(unittest.TestCase):

    def setUp(self) -> None:
        # Clean up database file before each test to ensure clean state
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

    def test_adding_new_api_key_yields_code_0(self):
        process = subprocess.run(RUN_CONTENT, capture_output=True)
        self.assertEqual(process.returncode, 0)

    def test_adding_new_api_key_with_already_existing_name_yields_return_code_1(self):
        subprocess.run(RUN_CONTENT, capture_output=True)
        process = subprocess.run(RUN_CONTENT, capture_output=True)
        self.assertEqual(process.returncode, 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
