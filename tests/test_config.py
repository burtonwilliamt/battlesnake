import unittest

import config


class TestTemporalBody(unittest.TestCase):

    def test_debug_off(self):
        self.assertFalse(config.DEBUG, 'DEBUG should be off in production.')

