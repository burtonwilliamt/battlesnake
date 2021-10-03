import cProfile
import tracemalloc
from src.planning.fringe import TimedBFS
from tests.test_fringe import make_root


def actual_work():
    root = make_root(depth = 10, branching=2, delay_ms=1)
    bfs = TimedBFS(root, 500)
    bfs.run()
    print(f'explored: {len(root.order_explored)}')
    print(f'slept: {root.time_slept}')


def main():
    tracemalloc.start()

    actual_work()

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    for stat in top_stats[:10]:
        print(stat)

if __name__ == '__main__':
    cProfile.run('main()', 'output.prof')