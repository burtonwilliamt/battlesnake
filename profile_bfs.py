import cProfile
import tracemalloc

from src.planning.fringe import TimedBFS, BoardState
from src.planning.simulation import Simulation
from tests.board_builder import BoardBuilder


def actual_work():
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
    sim = Simulation(board, max_depth=3)
    root = BoardState(sim)
    bfs = TimedBFS(root, 1000)
    bfs.run()


def main():
    tracemalloc.start()

    actual_work()

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    for stat in top_stats[:10]:
        print(stat)

if __name__ == '__main__':
    cProfile.run('main()', 'output.prof')