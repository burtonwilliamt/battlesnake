import unittest
from typing import Iterable
import time

from src.planning.fringe import BoardStateNode
from src.planning.timed_bfs import TimedBFS
from src.planning.simulation import BoardState

from tests.board_builder import BoardBuilder


class TestFringe(unittest.TestCase):

    def test_snake_decisions(self):
        board = BoardBuilder(
            '''
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            ''', {
                'a': 51,
                'b': 100,
                'c': 2,
                'd': 42,
            }).to_board()
        board_state = BoardState.from_board(board)
        root = BoardStateNode(board_state)
        bfs = TimedBFS(root, 500)
        start = time.time()
        bfs.run()
        end = time.time()
        print(f'Took {(end-start)*1000}ms')
        print(f'We expanded {bfs.num_expanded}')
        print(f'There are {len(bfs.q)} elements in the queue.')
