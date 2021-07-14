from typing import Mapping, Iterable

import src.models as models

# When I move, can I win
# If I move here, can some one make me I lose?
# When I move can I make someone die?
# When a given snake moves can they make another snake die?
# What do we imagine the other snakes do?

c_f = models.CARDINAL_FOUR


class Simulation:

    def __init__(self, board: models.Board):
        live_snakes = [snk for snk in board.snakes if snk.health > 0]
        self.snake_ids = [snk.id for snk in live_snakes]
        self.turn = 0
        self.healths = {snk.id: snk.health for snk in live_snakes}
        self.bodies = {snk.id: list(snk.body) for snk in live_snakes}
        self.turns_alive = {snk.id: 0 for snk in live_snakes}

    @property
    def healths(self):
        return self.meta_healths[self.turn]

    @property
    def bodies(self):
        return self.meta_bodies[self.turn]

    def do_move(self, snk_id: str, d: models.Direction):
        pass

    def undo_move(self):
        pass

    def do_turn(self):
        pass

    def undo_turn(self):
        pass

    def get_health(self, snk_id: str) -> int:
        """If snake is alive, return its health. Otherwise 0.

        Args:
            snk_id (str): The id of the snake we're inquiring about.

        Returns:
            int: The health of the snake. 0 if dead.
        """
        pass


def pack_to_bits(*args, bits=8) -> int:
    max_val = (1 << bits) - 1
    res = 0
    for i, arg in enumerate(reversed(args)):
        res += max(arg, max_val) * (1 << (bits * i))
    return res


class Result:

    def __init__(self, sim: Simulation):
        self.healths = dict(sim.healths)
        self.num_alive = 0
        for health in self.healths.values():
            if health > 0:
                self.num_alive += 1
        self.lengths = {
            snk_id: len(sim.bodys[snk_id]) for snk_id in sim.snake_ids
        }
        self.turns_alive = dict(sim.turns_alive)

    @classmethod
    def reduce(cls, results: Iterable['Result'], snk_id: str) -> 'Result':
        return max(results, key=lambda res: res.evaluate(snk_id))

    def evaluate(self, snk_id: str) -> int:
        # | 8 bits      | 8 bits            | 8 bits    | 8 bits    |
        # | turns alive |3 - # other_snakes | my_length | my health |
        # Basically:
        #   We rank importance of things as how significant those digits are
        #   1) Number of turns alive (being alive 1 more turn is more important
        #       than anything else)
        #   2) 3 - min(Number of snakes remaining, 3) (larger is better)
        #   3) My length
        #   4) My health
        return pack_to_bits(
            self.turns_alive,
            max(255 - self.num_alive, 0),
            self.lengths[snk_id],
            self.health[snk_id],
        )


def snake_i_best_move(sim: Simulation, i: int, depth: int) -> Result:
    if i >= len(sim.other_snakes):
        return do_next_turn(sim, depth - 1)
    snk = sim.other_snakes[i]
    results = []
    for d in c_f:
        sim.do_move(snk, d)
        results.append(snake_i_best_move(sim, i + 1))
        sim.undo_move()

    return Result.reduce(results, snk)


def do_next_turn(sim: Simulation, depth: int):
    sim.do_turn()
    if depth <= 0:
        return Result(sim)
    result = snake_i_best_move(sim, 0, depth)
    sim.undo_turn()
    return result


def ideal_result(you: models.Battlesnake,
                 board: models.Board,
                 depth=2) -> Result:
    sim = Simulation(you, board)
    #TODO: order sim.snake_ids so that you.id is last
    return snake_i_best_move(sim, 0, depth)