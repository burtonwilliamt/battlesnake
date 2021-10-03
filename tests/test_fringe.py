import unittest
from typing import Iterable
import time

from src.planning.fringe import TimedBFS, ChildGenerator


def make_root(depth=10, delay_ms=1, branching=1):
    class ChildGeneratorFake(ChildGenerator):
        next_id = 0
        time_slept = 0
        order_explored = []

        def __init__(self, depth, delay_ms, branching):
            self.depth = depth
            self.delay_ms = delay_ms
            self.branching = branching
            self.my_id = self.__class__.next_id
            self.__class__.next_id += 1

        def children(self) -> Iterable[ChildGenerator]:
            self.order_explored.append(self.my_id)
            for _ in range(self.branching):
                if self.depth == 1:
                    return
                self.__class__.time_slept += 1
                time.sleep(.001 * self.delay_ms)
                child = ChildGeneratorFake(self.depth - 1, self.delay_ms,
                                        self.branching)
                yield child

    return ChildGeneratorFake(depth, delay_ms, branching)


class TestFringe(unittest.TestCase):

    def test_bfs_basic(self):
        root = make_root(depth=3)

        bfs = TimedBFS(root, 500)
        bfs.run()
        self.assertSequenceEqual(root.order_explored, [0,1,2])

    def test_bfs_branching(self):
        root = make_root(depth=3, branching=2)

        bfs = TimedBFS(root, 500)
        bfs.run()
        self.assertSequenceEqual(root.order_explored, [0, 1,2, 3,4, 5,6])

    def test_bfs_ends_early(self):
        root = make_root(depth=10, branching=2, delay_ms=1)

        bfs = TimedBFS(root, 30)
        start = time.time()
        bfs.run()
        end = time.time()
        self.assertLessEqual(1000*(end-start), 30)

        # should expand at most 30 nodes
        self.assertLessEqual(len(root.order_explored), 30)
        # not strictly guranateed but under normal conditions this is expected
        self.assertGreaterEqual(root.time_slept, 15)

        # the nodes should still be in order
        self.assertSequenceEqual(root.order_explored, range(len(root.order_explored)))