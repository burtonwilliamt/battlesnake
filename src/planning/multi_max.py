from typing import Iterable, Tuple

import src.models as models

from src.planning.simulation import Simulation

# When I move, can I win
# If I move here, can some one make me I lose?
# When I move can I make someone die?
# When a given snake moves can they make another snake die?
# What do we imagine the other snakes do?

c_f = models.CARDINAL_FOUR


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

    @classmethod
    def reduce(cls, results: Iterable['Result'], snk_id: int) -> 'Result':
        return max(results, key=lambda res: res.evaluate(snk_id))

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


def snake_i_best_move(sim: Simulation, snk_id: int,
                      depth: int) -> Tuple[Result, models.Direction]:
    if snk_id >= len(sim.snake_ids):
        result, direction = do_next_turn(sim, depth - 1)
        return result, direction

    # If this snake is dead, just let the other snakes play.
    if sim.snake_is_dead(snk_id):
        others_result, _ = snake_i_best_move(sim, snk_id + 1, depth)
        return others_result, None

    # Try moving each direction
    best_result = None
    best_direction = None
    for d in c_f:
        sim.do_move(snk_id, d)
        result, _ = snake_i_best_move(sim, snk_id + 1, depth)
        if best_result is None or result.evaluate(
                snk_id) > best_result.evaluate(snk_id):
            best_result = result
            best_direction = d
        sim.undo_move(snk_id)

    return best_result, best_direction


def do_next_turn(sim: Simulation,
                 depth: int) -> Tuple[Result, models.Direction]:
    sim.do_turn()
    if depth <= 0:
        result = Result(sim)
        sim.undo_turn()
        return result, None
    result, direction = snake_i_best_move(sim, 0, depth)
    sim.undo_turn()
    return result, direction


def ideal_direction(board: models.Board, depth=3) -> models.Direction:
    sim = Simulation(board, max_depth=depth)
    #TODO: order sim.snake_ids so that you.id is last
    _, best_direction = snake_i_best_move(sim, 0, depth)
    return best_direction