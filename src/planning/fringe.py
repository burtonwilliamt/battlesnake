from typing import Iterable, Tuple, List, Mapping
import signal
import time
import copy

import src.models as models
import config

from src.planning.simulation import Simulation

# from one board state with 4 snakes, there are 4 * 4 * 4 * 4 possible new board states

# we can assume every snake will not double back on their "neck"

# More formally, a multi-max solution that assumes each snake considers all 4
# moves will result in the same outcome if it only consideres the 3 moves
# excluding the "neck eater"

# The multi-max solution is the one where each node chooses the best outcome,
# assuming opponets would subsequently also choose the best outcome.

# For a novel solution to come from including the option to "eat oneself" there
# would have to be a snake that chooses to eat themselves. Otherwise, the
# solution is the same either way. However, to "eat oneself" clearly violates
# the rationality assumtion, as there is no way that eating the neck is strictly
# better than an alternative. At best, it's equivalent to dying by some other choice.

# Therefore we can reduce the expansion to 3 * 3 * 3 *3 possible new board states.

# Goal 1: never exceed the time limit
# Goal 2: Explore as many useful options as possible
#   a) deeply exploring one option is not as good as shallowly exploring many
#      for example, looking 100 moves ahead after moving right, but not
#      considering moving left
# This implies that we want to explore breadth first, not depth first


class ChildGenerator:
    def children(self) -> Iterable["ChildGenerator"]:
        pass


class TimedBFS:
    CLEANUP_TIME_MS = 2

    def __init__(self, root_node: ChildGenerator, limit_ms: int):
        self.limit_ms = limit_ms
        assert (
            self.limit_ms > self.CLEANUP_TIME_MS,
            f"Limit must be greater than {self.CLEANUP_TIME_MS}ms.",
        )

        self.q = list()
        self.q.append(root_node)
        self.num_expanded = 0

    def run(self):
        def handler(signum, frame):
            raise TimeoutError("Ok, we're out of time. Wrap it up.")

        # Set the signal handler and an alarm
        signal.signal(signal.SIGALRM, handler)
        # Leave time to cleanup at the end
        signal.setitimer(
            signal.ITIMER_REAL, 0.001 * (self.limit_ms - self.CLEANUP_TIME_MS)
        )

        try:
            while len(self.q) > 0:
                node = self.q.pop(0)
                for child in node.children():
                    self.q.append(child)
                self.num_expanded += 1
        except TimeoutError:
            return
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)


def snake_decision_or_board_state(sim: Simulation, snk_id: int):
    # Base condition, if we did all the snakes then do a turn.
    if snk_id >= len(sim.snake_ids):
        try:
            sim.do_turn()
        except AssertionError:
            print(sim.turn)
            print(sim.snake_is_dead(1))
            print(sim._t_move_choices[0 : sim.turn + 1])
            print(sim._t_health[0 : sim.turn + 1])
            raise

        return BoardState(sim)
    else:
        return SnakeDecision(sim, snk_id)


class SnakeDecision(ChildGenerator):
    def __init__(self, sim: Simulation, snk_id: int):
        self.indent = "\t" * snk_id
        self.sim = sim
        self.snk_id = snk_id
        self.moves = None

    def move(self, direction: models.Direction) -> ChildGenerator:
        child_sim = copy.deepcopy(self.sim)
        child_sim.do_move(self.snk_id, direction)
        child = snake_decision_or_board_state(child_sim, self.snk_id + 1)
        return child

    def make_moves(self) -> None:
        self.moves = {}
        # If this snake is dead, just let the other snakes play.
        if self.sim.snake_is_dead(self.snk_id):
            child = snake_decision_or_board_state(self.sim, self.snk_id + 1)
            for direction in models.CARDINAL_FOUR:
                self.moves[direction] = child
            return

        # Try moving each direction.
        for direction in models.CARDINAL_FOUR:
            self.moves[direction] = self.move(direction)

    def safe_children(self, child: ChildGenerator) -> Iterable[ChildGenerator]:
        if isinstance(child, BoardState):
            yield child
        else:
            for sub_child in child.children():
                yield sub_child

    def children(self) -> Iterable[ChildGenerator]:
        # If we don't have any moves yet, generate them
        if self.moves is None:
            self.make_moves()

        # If we are dead then all moves have equivalent value
        if self.sim.snake_is_dead(self.snk_id):
            child = self.moves[models.UP]
            for sub_child in self.safe_children(self.moves[models.UP]):
                yield sub_child
            return

        for direction, child in self.moves.items():
            # If we are the last SnakeDecision node, yield children directly
            for sub_child in self.safe_children(child):
                yield sub_child


class BoardState(ChildGenerator):
    def __init__(self, sim: Simulation):
        self.sim = copy.deepcopy(sim)
        self.root = None

    def children(self) -> Iterable[ChildGenerator]:
        if self.root is None:
            self.root = SnakeDecision(self.sim, 0)
        for n in self.root.children():
            yield n
