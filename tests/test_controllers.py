import sys
sys.path.append('.')
import unittest

from server.fleetman_http_api.controllers import *


class TestControllers(unittest.TestCase):

    def test_nothing(self):
        self.assertEqual(1, 1)


if __name__=="__main__":
    unittest.main()
