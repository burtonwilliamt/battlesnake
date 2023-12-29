from typing import Iterable, Tuple, List, Mapping

import src.models as models
import config

from src.planning.simulation import Simulation


def pack_to_bits(*args, bits=8) -> int:
    max_val = (1 << bits) - 1
    res = 0
    for i, arg in enumerate(reversed(args)):
        res += min(arg, max_val) * (1 << (bits * i))
    return res


class Result:
    def __init__(self, sim: Simulation):
        self.healths = list(sim.healths)
        self.num_dead = 0
        for health in self.healths:
            if health == 0:
                self.num_dead += 1
        self.lengths = [len(sim.bodies[snk_id]) for snk_id in sim.snake_ids]
        self.turns_alive = {snk_id: sim.turns_alive(snk_id) for snk_id in sim.snake_ids}

        self.sim_render = None
        if config.DEBUG:
            self.sim_render = sim.render()

    def evaluate_for(self, snk_id: str) -> int:
        # | 8 bits      | 8 bits        | 8 bits    | 8 bits    |
        # | turns alive | # dead snakes | my_length | my health |
        # Basically:
        #   We rank importance of things as how significant those digits are
        #   1) Staying alive. Obviously.
        #   2) More snakes dead (KILL ALL HUMANS, or snakes whatever.)
        #   3) My length
        #   4) My health
        return pack_to_bits(
            self.turns_alive[snk_id],
            self.num_dead,
            self.lengths[snk_id],
            self.healths[snk_id],
        )

    def __eq__(self, other):
        if not isinstance(other, Result):
            return False

        return (
            self.healths == other.healths
            and self.num_dead == other.num_dead
            and self.lengths == other.lengths
        )


class DecisionNode:
    def get_result(self) -> Result:
        raise NotImplementedError

    def node_evaluate_for(self, snk_id: int) -> int:
        return self.get_result().evaluate_for(snk_id)


class LeafNode(DecisionNode):
    ResultType = Result

    def __init__(self, sim: Simulation):
        self._result = self.ResultType(sim)

    def get_result(self) -> Result:
        return self._result


class SnakeDecision(DecisionNode):
    LeafNodeType = LeafNode

    def __init__(self, *, best_result, best_direction):
        self._best_direction = best_direction
        self._best_result = best_result

    def get_result(self) -> Result:
        return self._best_result

    def get_best_direction(self) -> models.Direction:
        return self._best_direction

    @classmethod
    def _process_turn(cls, sim: Simulation, depth: int) -> DecisionNode:
        sim.do_turn()
        if depth <= 0:
            node = cls.LeafNodeType(sim)
        else:
            node = cls._process_snk_id_at_depth(sim, 0, depth)
        sim.undo_turn()
        return node

    @classmethod
    def _process_snk_id_at_depth(
        cls, sim: Simulation, snk_id: int, depth: int
    ) -> DecisionNode:
        # Base condition, if we did all the snakes then do a turn.
        if snk_id >= len(sim.snake_ids):
            return cls._process_turn(sim, depth - 1)

        # If this snake is dead, just let the other snakes play.
        if sim.snake_is_dead(snk_id):
            return cls._process_snk_id_at_depth(sim, snk_id + 1, depth)

        # Try moving each direction.
        best_value = None
        best_direction = None
        best_result = None
        for d in models.CARDINAL_FOUR:
            if sim.is_obvious_death(snk_id, d):
                child = cls.LeafNodeType(sim)
            else:
                sim.do_move(snk_id, d)
                child = cls._process_snk_id_at_depth(sim, snk_id + 1, depth)
                sim.undo_move(snk_id)

            value = child.node_evaluate_for(snk_id)
            if best_value is None or value > best_value:
                best_direction = d
                best_value = value
                best_result = child.get_result()

        return cls(best_result=best_result, best_direction=best_direction)

    @classmethod
    def make_tree(cls, sim: Simulation, depth: int):
        return cls._process_snk_id_at_depth(sim, 0, depth)


def ideal_direction(board: models.Board, depth=3) -> models.Direction:
    # TODO: require snk_id
    sim = Simulation(board, max_depth=depth)
    root = SnakeDecision.make_tree(sim, depth)
    return root.get_best_direction()
