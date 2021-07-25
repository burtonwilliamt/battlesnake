import unittest
from typing import List

from src.planning.temporal_body import TemporalBody


class TestTemporalBody(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.tb = TemporalBody([1,2,3])

    def test_len(self):
        self.assertEqual(len(self.tb), 3)

    def test_head(self):
        self.assertEqual(self.tb.head(), 1)

    def test_tail(self):
        self.assertEqual(self.tb.tail(), 3)

    def test_iter(self):
        self.assertSequenceEqual([elem for elem in self.tb], [1,2,3])

    def check_equal(self, tb:TemporalBody, l:List[int]):
        self.assertEqual(len(tb), len(l))
        self.assertEqual(tb.head(), l[0])
        self.assertEqual(tb.tail(), l[-1])
        self.assertSequenceEqual(list(tb), l)

    def test_add_head(self):
        self.tb.add_head(0)
        self.check_equal(self.tb, [0,1,2,3])

    def test_del_head(self):
        self.tb.del_head()
        self.check_equal(self.tb, [2,3])

    def test_del_tail(self):
        self.tb.del_tail()
        self.check_equal(self.tb, [1,2])

    def test_undo_del_tail(self):
        self.tb.del_tail()
        self.check_equal(self.tb, [1,2])
        self.tb.del_tail()
        self.check_equal(self.tb, [1])

        self.tb.undo_del_tail()
        self.check_equal(self.tb, [1,2])
        self.tb.undo_del_tail()
        self.check_equal(self.tb, [1,2,3])

    def test_grow(self):
        self.tb.grow()
        self.check_equal(self.tb, [1,2,3,3])

    def test_undo_grow(self):
        self.tb.grow()
        self.check_equal(self.tb, [1,2,3,3])
        self.tb.undo_grow()
        self.check_equal(self.tb, [1,2,3])

    def test_history_separate(self):
        self.tb.del_tail()
        self.check_equal(self.tb, [1,2])
        self.tb.grow()
        self.check_equal(self.tb, [1,2,2])
        self.tb.undo_grow()
        self.check_equal(self.tb, [1,2])
        self.tb.undo_del_tail()
        self.check_equal(self.tb, [1,2,3])


