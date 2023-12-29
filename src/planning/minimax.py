from src import models
from src.planning.simulation import Simulation


def evaluate(sim: Simulation) -> int:
    """Returns the minimax value function for this sim state.
    
    Our snake is assumed to be the first snake (simple_id = 0).

    Currently, this returns the bit ordering `I'm alive | You're dead`. This
    will reward me for staying alive, and maybe killing you. It will reward you
    for killing me, and maybe staying alive (pessimistic about kamakazi snakes).
    """
    IM_ALIVE = 0b10
    YOURE_DEAD = 0b01
    return (IM_ALIVE if sim.healths[0] > 0 else 0) | (YOURE_DEAD if sim.healths[1] == 0 else 0)


def ideal_direction(board: models.Board, depth: int) -> models.Direction:
    sim = Simulation(board, max_depth=depth)
    if len(sim.snake_ids) != 2:
        raise ValueError("Minimax does not support boards with more than two snakes yet.")