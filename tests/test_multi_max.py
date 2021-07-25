import unittest

import src.planning.multi_max

class TestMultiMax(unittest.TestCase):

    def test_pack_to_bits(self):
        self.assertEqual(bin(src.planning.multi_max.pack_to_bits(255, 300, 69, 0)),
                         bin(0b11111111_11111111_01000101_00000000))


