import os
import sys
import subprocess
import unittest

import coverage


TEST_DIR_NAME = "tests"

OMITTED_FILES = [
    "__init__.py",
    "*/models/*",
    "fleet_management_api/controllers/*",
    "util.py",
    "typing_utils.py",
    "encoder.py"
]

HTML_REPORT_FLAG = "-h"


def _report_coverage(cov: coverage.Coverage) -> None: # pragma: no cover
    if HTML_REPORT_FLAG in sys.argv:
        cov.html_report()
        subprocess.run(["open", "htmlcov/index.html"])
    else:
        cov.report()


def _run_tests(show_test_names: bool = True) -> None: # pragma: no cover
    possible_paths = [os.path.join(TEST_DIR_NAME,path) for path in sys.argv[1:]]
    paths = [path for path in possible_paths if os.path.exists(path)]
    if not paths:
        paths = [TEST_DIR_NAME]
    suite = unittest.TestSuite()
    for path in paths:
        if os.path.isfile(path):
            file_name = os.path.basename(path)
            if file_name.endswith(".py"):
                pattern, dir = file_name, os.path.dirname(path)
        else:
            pattern, dir = "test_*.py", path
        suite.addTests(unittest.TestLoader().discover(dir, pattern=pattern))
    verbosity = 2 if show_test_names else 1
    unittest.TextTestRunner(verbosity=verbosity, buffer=True).run(suite)


if __name__ == "__main__":  # pragma: no cover
    cov = coverage.Coverage(branch=True, omit=OMITTED_FILES)
    cov.start()
    _run_tests()
    cov.stop()
    cov.save()
    _report_coverage(cov)


