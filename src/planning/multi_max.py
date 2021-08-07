from typing import Iterable, Tuple, List, Mapping

import src.models as models

from src.planning.simulation import Simulation

# When I move, can I win
# If I move here, can some one make me I lose?
# When I move can I make someone die?
# When a given snake moves can they make another snake die?
# What do we imagine the other snakes do?

c_f = models.CARDINAL_FOUR

DEBUG = True


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
        if DEBUG:
            self.sim_render = sim.render()

    def evaluate(self, snk_id: str) -> int:
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

        return (self.healths == other.healths and
                self.num_dead == other.num_dead and
                self.lengths == other.lengths)


class DecisionNode:
    def get_result(self) -> Result:
        raise NotImplementedError

    def node_evaluate(self, snk_id:int) -> int:
        result = self.get_result()
        return result.evaluate(snk_id)


class LeafNode(DecisionNode):
    def __init__(self, sim:Simulation):
        self.result = Result(sim)
        self.turn = sim.turn

    def get_result(self) -> Result:
        return self.result


class SnakeDecision(DecisionNode):
    def __init__(self, *, snk_id:int, turn:int, moves:Mapping[models.Direction, DecisionNode]):
        self.snk_id = snk_id
        self.turn = turn

        self.moves = moves
        for d in models.CARDINAL_FOUR:
            if d not in moves:
                raise AssertionError('The moves mapping should have all directions.')

        self.best_direction = self._find_best_direction()

    def _find_best_direction(self) -> models.Direction:
        best_value = None
        best_direction = None
        for d in models.CARDINAL_FOUR:
            value = self.moves[d].node_evaluate(self.snk_id)
            if best_value is None or value > best_value:
                best_direction = d
                best_value = value
        return best_direction

    def get_result(self) -> Result:
        return self.moves[self.best_direction].get_result()

    @classmethod
    def _process_turn(cls, sim:Simulation, depth:int) -> DecisionNode:
        sim.do_turn()
        if depth <= 0:
            node = LeafNode(sim)
            sim.undo_turn()
            return node
        node = cls._process_snk_id_at_depth(sim, 0, depth)
        sim.undo_turn()
        return node

    @classmethod
    def _process_snk_id_at_depth(cls, sim: Simulation, snk_id: int,
                      depth: int) -> DecisionNode:
        # Base condition, if we did all the snakes then do a turn.
        if snk_id >= len(sim.snake_ids):
            node = cls._process_turn(sim, depth - 1)
            return node

        # If this snake is dead, just let the other snakes play.
        if sim.snake_is_dead(snk_id):
            node = cls._process_snk_id_at_depth(sim, snk_id + 1, depth)
            return node

        # Try moving each direction.
        moves = {}
        for d in models.CARDINAL_FOUR:
            sim.do_move(snk_id, d)
            moves[d] = cls._process_snk_id_at_depth(sim, snk_id + 1, depth)
            sim.undo_move(snk_id)

        return cls(snk_id=snk_id, turn=sim.turn, moves=moves)

    @classmethod
    def make_tree(cls, sim: Simulation, depth: int):
        return cls._process_snk_id_at_depth(sim, 0, depth)


def ideal_direction(board: models.Board, depth=3) -> models.Direction:
    # TODO: require snk_id
    sim = Simulation(board, max_depth=depth)
    root = SnakeDecision.make_tree(sim, depth)
    return root.best_direction