import sys
import subprocess
import unittest

import coverage


OMITTED_FILES = [
    "__init__.py",
    "*/models/*",
    "fleet_management_api/controllers/*",
    "util.py",
    "typing_utils.py",
    "encoder.py"
]


cov = coverage.Coverage(branch=True, omit=OMITTED_FILES)
cov.start()

suite = unittest.TestLoader().discover('tests', pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)

cov.stop()
cov.save()

if len(sys.argv)>1 and sys.argv[1] == "-h":
    cov.html_report()
    subprocess.run(["open", "htmlcov/index.html"])
else:
    cov.report()
