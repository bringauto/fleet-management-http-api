import unittest

import coverage


cov = coverage.Coverage()
cov.start()

suite = unittest.TestLoader().discover('tests', pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)

cov.stop()
cov.save()

cov.report(
    omit=[
        "__init__.py",
        "*/models/*",
        "*/controllers/*",
        "util.py",
        "typing_utils.py",
        "encoder.py"
    ]
)
