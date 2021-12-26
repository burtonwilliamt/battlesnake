# import tracemalloc
import cProfile

from src.planning.fringe import BoardStateNode
from src.planning.timed_bfs import TimedBFS
from src.planning.simulation import BoardState

from tests.board_builder import BoardBuilder


def main():
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
    bfs.run()
    print(f'We expanded {bfs.num_expanded}')
    print(f'There are {len(bfs.q)} elements in the queue.')


if __name__ == '__main__':
    cProfile.run('main()', 'output.prof')