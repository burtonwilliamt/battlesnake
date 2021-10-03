from typing import Iterable, Tuple, List, Mapping
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
    def children(self) -> Iterable['ChildGenerator']:
        pass


class TimedBFS:

    def __init__(self, root_node:ChildGenerator, limit_ms:int):
        self.termination_time = time.time() + limit_ms*.001

        self.q = list()
        self.q.append(root_node)

    def out_of_time(self) -> bool:
        if time.time() >= self.termination_time:
            return True
        return False

    def run(self):
        while not self.out_of_time() and len(self.q) > 0:
            node = self.q.pop(0)
            for child in node.children():
                self.q.append(child)


def snake_decision_or_board_state(sim:Simulation, snk_id: int):
    # Base condition, if we did all the snakes then do a turn.
    if snk_id >= len(sim.snake_ids):
        sim.do_turn()
        return BoardState(sim)
    else:
        return SnakeDecision(sim, snk_id)


class SnakeDecision(ChildGenerator):
    def __init__(self, sim:Simulation, snk_id: int):
        self.sim = sim
        self.snk_id = snk_id
        self.moves = None
        self.is_dead = sim.snake_is_dead(self.snk_id)

    def move(self, direction:models.Direction) -> ChildGenerator:
        child_sim = copy.deepcopy(self.sim)
        child_sim.do_move(self.snk_id, direction)
        child = snake_decision_or_board_state(child_sim, self.snk_id + 1)
        return child

    def make_moves(self) -> None:
        self.moves = {}
        # If this snake is dead, just let the other snakes play.
        if self.is_dead:
            child = snake_decision_or_board_state(self.sim, self.snk_id+1)
            for direction in models.CARDINAL_FOUR:
                self.moves[direction] = child

        # Try moving each direction.
        for direction in models.CARDINAL_FOUR:
            self.moves[direction] = self.move(direction)

    def children(self) -> Iterable[ChildGenerator]:
        # If we don't have any moves yet, generate them
        if self.moves is None:
            self.make_moves()

        # If we are dead then all moves have equivalent value
        if self.is_dead:
            for sub_child in self.moves[models.UP].children():
                yield sub_child
            return

        for child in self.moves.items():
            # If we are the last SnakeDecision node, yield children directly
            if isinstance(child, BoardState):
                yield child
                continue
            for sub_child in child.children():
                yield sub_child


class BoardState(ChildGenerator):
    def __init__(self, sim:Simulation):
        self.sim = copy.deepcopy(sim)
        self.root = None

    def children(self) -> Iterable[ChildGenerator]:
        if self.root is None:
            self.root = SnakeDecision(self.sim, 0)
        for n in self.root.children():
            yield n
