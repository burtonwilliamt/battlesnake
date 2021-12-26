from typing import Iterable, Tuple, List, Mapping
import itertools
from src.planning.timed_bfs import ChildGenerator

import src.models as models

from src.planning.simulation import BoardState


class BoardStateNode(ChildGenerator):

    def __init__(self, board: BoardState):
        self.board = board

    def children(self) -> Iterable[ChildGenerator]:
        for move_set in itertools.combinations_with_replacement(models.CARDINAL_FOUR, len(self.board.snakes)):
            if self.quick_skip(move_set):
                continue
            yield BoardStateNode(self.board.do_turn(move_set))

    def quick_skip(self, move_set:Tuple[models.Direction]) -> bool:
        """Should we skip this move set?

        This is used to prevent 'dumb' moves. For example, moving onto your neck.

        Args:
            move_set (Tuple[models.Direction]): The moves the snakes are doing,
            in order of the snakes.

        Returns:
            bool: Whether we should skip this move set.
        """
        return False
