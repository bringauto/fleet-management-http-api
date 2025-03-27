import os
import unittest
import subprocess


RUN_CONTENT = [
    "python",
    "scripts/add_api_key.py",
    "Alice",
    "tests/script_args/test_config.json",
    "-t",
    "db_file.db",
]


class Test_Running_New_API_Key_Script(unittest.TestCase):

    def test_adding_new_api_key_yields_code_0(self):
        process = subprocess.run(RUN_CONTENT, stdout=True)
        self.assertEqual(process.returncode, 0)

    def test_adding_new_api_key_with_already_existing_name_yields_return_code_1(self):
        subprocess.run(RUN_CONTENT, capture_output=True)
        process = subprocess.run(RUN_CONTENT, capture_output=True)
        self.assertEqual(process.returncode, 1)

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.exists("db_file.db"):
            os.remove("db_file.db")


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
