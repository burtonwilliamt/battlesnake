from typing import Iterable
import signal


class ChildGenerator:
    """The nodes for TimedBFS have to be able to generate children.

    When BFS "visits" a node, it fetches all the children and adds them to the
    queue.
    """

    def children(self) -> Iterable['ChildGenerator']:
        pass


class TimedBFS:
    """Search through generated nodes using BFS with a search time limit."""

    CLEANUP_TIME_MS = 2

    def __init__(self, root_node: ChildGenerator, limit_ms: int):
        self.limit_ms = limit_ms
        assert self.limit_ms > self.CLEANUP_TIME_MS, f'Limit must be greater than {self.CLEANUP_TIME_MS}ms.'

        self.q = list()
        self.q.append(root_node)
        self.num_expanded = 0

    def run(self):

        def handler(signum, frame):
            raise TimeoutError('Ok, we\'re out of time. Wrap it up.')

        # Set the signal handler and an alarm
        signal.signal(signal.SIGALRM, handler)
        # Leave time to cleanup at the end
        signal.setitimer(signal.ITIMER_REAL,
                         .001 * (self.limit_ms - self.CLEANUP_TIME_MS))

        try:
            while len(self.q) > 0:
                node = self.q.pop(0)
                count = 0
                for child in node.children():
                    count += 1
                    self.q.append(child)
                self.num_expanded += 1
        except TimeoutError:
            return
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
