from typing import Iterable, Tuple, List, Mapping
from src.planning.timed_bfs import ChildGenerator

import src.models as models

from src.planning.simulation import BoardState

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


class TurnBuilder:

    def __init__(self, board: BoardState, moves: Tuple[models.Direction]):
        self.board = board
        self.moves = moves

    def do_move(self, snk_id: int, d: models.Direction) -> 'TurnBuilder':
        assert self.board.turn < BoardState.MAX_LOOKAHEAD, 'Cannot call do_move when simulation is at max depth.'
        assert snk_id == len(self.moves), 'Must declare snake moves in order'
        assert snk_id >= 0 and snk_id < len(
            self.board.snakes), 'Snake id must be in range'
        assert ((self.board.snakes[snk_id].health != 0 and d is not None) or
                (self.board.snakes[snk_id].health == 0 and
                 d is None)), 'Dead snakes move None'
        return TurnBuilder(self.board, tuple((*self.moves, d)))

    def do_turn(self) -> BoardState:
        return self.board.do_turn(self.moves)



def snake_decision_or_board_state(builder: TurnBuilder, snk_id: int):
    # Base condition, if we did all the snakes then do a turn.
    if snk_id >= len(builder.board.snakes):
        return BoardStateNode(builder.do_turn())
    else:
        return SnakeDecision(builder, snk_id)


class SnakeDecision(ChildGenerator):

    def __init__(self, builder: TurnBuilder, snk_id: int):
        self.builder = builder
        self.snk_id = snk_id
        self.moves = None

    def is_dead(self) -> bool:
        return self.builder.board.snakes[self.snk_id].health == 0

    def move(self, direction: models.Direction) -> ChildGenerator:
        new_builder = self.builder.do_move(self.snk_id, direction)
        return snake_decision_or_board_state(new_builder, self.snk_id + 1)

    def make_moves(self) -> None:
        self.moves = {}
        # If this snake is dead, just let the other snakes play.
        if self.is_dead():
            new_builder = self.builder.do_move(self.snk_id, None)
            child = snake_decision_or_board_state(new_builder, self.snk_id + 1)
            for direction in models.CARDINAL_FOUR:
                self.moves[direction] = child
            return

        # Try moving each direction.
        for direction in models.CARDINAL_FOUR:
            self.moves[direction] = self.move(direction)

    def safe_children(self, child:ChildGenerator) -> Iterable[ChildGenerator]:
        if isinstance(child, BoardStateNode):
            yield child
        else:
            for sub_child in child.children():
                yield sub_child

    def children(self) -> Iterable[ChildGenerator]:
        # If we don't have any moves yet, generate them
        if self.moves is None:
            self.make_moves()

        # If we are dead then all moves have equivalent value
        if self.is_dead():
            #print('Dead')
            child = self.moves[models.UP]
            for sub_child in self.safe_children(self.moves[models.UP]):
                yield sub_child
            return

        for child in self.moves.values():
            #print('Alive')
            for sub_child in self.safe_children(child):
                yield sub_child


class BoardStateNode(ChildGenerator):

    def __init__(self, board: BoardState):
        self.board = board
        self.root = None

    def children(self) -> Iterable[ChildGenerator]:
        if self.root is None:
            self.root = SnakeDecision(TurnBuilder(self.board, ()), 0)
        for n in self.root.children():
            yield n
