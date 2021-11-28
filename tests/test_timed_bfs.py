import unittest
from typing import Iterable
import time

from src.planning.timed_bfs import ChildGenerator, TimedBFS


class TestingGenerator(ChildGenerator):
    """A ChildGenerator for writing tests.

    This requires you to provide the children at construction time.
    It also keeps track of if .children() has been called.
    """
    visited_count = 0

    def __init__(self, children:Iterable[ChildGenerator], delay_ms:int = 0):
        self._provided_children = children
        self.delay_ms = delay_ms
        self.visited_seq_id = None

    def children(self) -> Iterable[ChildGenerator]:
        for child in self._provided_children:
            yield child
        self.visited_seq_id = TestingGenerator.visited_count
        TestingGenerator.visited_count += 1
        time.sleep(.001 * self.delay_ms)


class TestTimedBFS(unittest.TestCase):
    def setUp(self) -> None:
        TestingGenerator.visited_count = 0
        return super().setUp()

    def test_visits_all_children_in_order(self):
        """Make sure the bfs is actually doing a bfs."""
        #       root
        #   /         \
        #  left_mid   right
        #    |
        #  left_leaf
        left_leaf = TestingGenerator([])
        left_mid = TestingGenerator([left_leaf])
        right = TestingGenerator([])
        root = TestingGenerator([left_mid, right])

        bfs = TimedBFS(root, limit_ms=10_000)
        bfs.run()

        self.assertEqual(bfs.num_expanded, 4)

        self.assertEqual(root.visited_seq_id, 0)
        self.assertEqual(left_mid.visited_seq_id, 1)
        self.assertEqual(right.visited_seq_id, 2)
        self.assertEqual(left_leaf.visited_seq_id, 3)

    def test_returns_after_timeout(self):
        """TimedBFS roughly respects the requested limit."""
        left = TestingGenerator([], delay_ms=1000)
        right = TestingGenerator([])
        root = TestingGenerator([left, right])

        bfs = TimedBFS(root, limit_ms=100)
        start = time.time()
        bfs.run()
        end = time.time()
        # Bad practice, but we're going to test that this takes roughly the
        # expected amount of time.
        self.assertLessEqual(1000*(end-start), 100 + 10)
        self.assertGreaterEqual(1000*(end-start), 100 - 10)

        # Only one node gets fully expanded (root)
        # before left is interupted 100ms into its 1000ms delay
        self.assertEqual(bfs.num_expanded, 1)

        self.assertEqual(root.visited_seq_id, 0)
        # Sequence is set before delay, so left still has number.
        self.assertEqual(left.visited_seq_id, 1)
        self.assertEqual(right.visited_seq_id, None)
