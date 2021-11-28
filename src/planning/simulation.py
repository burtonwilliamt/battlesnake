from typing import Iterable, Mapping, List, Tuple

import src.models as models

MAX_HEALTH = 100


class SimpleSnake:

    __slots__ = ('health', 'body')

    def __init__(self, health: int, body: List[Tuple[int, int]]):
        self.health = health
        self.body = body

    def copy(self):
        return SimpleSnake(self.health, list(self.body))


class BoardState:
    """An immutable board state.

    You can access attributes on this state, or
    create a new mutated version using do_turn.
    """

    __slots__ = ('height', 'width', 'snakes', 'food', 'turn', 'max_depth')

    def __init__(self, height: int, width: int, snakes: Tuple[SimpleSnake],
                 food: List[Tuple[int, int]], turn: int, max_depth: int):
        self.height = height
        self.width = width
        self.snakes = snakes
        self.food = food
        self.turn = turn
        self.max_depth = max_depth

    @classmethod
    def from_board(cls, board:models.Board, max_depth:int) -> 'BoardState':
        snakes = []
        for heavy_snake in board.snakes:
            body = [(segment.x, segment.y) for segment in heavy_snake.body]
            snakes.append(SimpleSnake(heavy_snake.health, body))
        food = [(food.x, food.y) for food in board.food]
        return BoardState(board.height, board.width, snakes, food, 0, max_depth)

    def copy(self) -> 'BoardState':
        return BoardState(
            self.height,
            self.width,
            tuple(snake.copy() for snake in self.snakes),
            list(self.food),
            self.turn,
            self.max_depth,
        )

    def _actually_do_turn(self, moves: Tuple[models.Direction]) -> None:
        assert (self.turn < self.max_depth,
                'Cannot call do_turn when simulation is at max depth.')
        assert (len(moves) == len(self.snakes), 'All snakes need a move.')
        self._moveSnakes(moves)

        self._reduceSnakeHealth()
        self._maybeFeedSnakes()
        self._maybeEliminateSnakes()
        self.turn += 1

    def do_turn(self, moves: Tuple[models.Direction]) -> 'BoardState':
        """Make a copy of this board state, and perform these moves."""
        new = self.copy()
        new._actually_do_turn(moves)
        return new

    def _moveSnakes(self, moves: Tuple[models.Direction]):
        for move, snake in zip(moves, self.snakes):
            # Skip dead snakes
            if snake.health == 0:
                continue

            d = move
            new_head = (snake.body[0][0] + d.rel_x, snake.body[0][1] + d.rel_y)
            snake.body.insert(0, new_head)
            snake.body.pop(-1)

    def _reduceSnakeHealth(self):
        for snake in self.snakes:
            if snake.health > 0:
                snake.health -= 1

    def _maybeFeedSnakes(self):
        for i in range(len(self.food) - 1, -1, -1):
            food = self.food[i]
            food_eaten = False
            for snake in self.snakes:
                # Dead snakes can't eat
                if snake.health == 0:
                    continue

                if snake.body[0][0] == food[0] and snake.body[0][1] == food[1]:
                    food_eaten = True
                    snake.health = MAX_HEALTH
                    snake.body.append(snake.body[-1])
            if food_eaten:
                self.food.pop(i)

    def _maybeEliminateSnakes(self):
        # Snakes that starve or go out of bounds die first
        for snake in self.snakes:
            # Skip already eliminated snakes
            if snake.health == 0:
                continue
            # Check for bounds
            if self._snakeIsOutOfBounds:
                snake.health = 0

        # All remaining eliminations happen simultaneously
        # This is so that eliminated snakes cause others to be eliminated
        collisions = []
        for snake in self.snakes:
            # Skip dead snakes
            if snake.health == 0:
                continue
            # Check for body
            elif self._snakeHasBodyCollided(snake):
                collisions.append(snake)
            # Check for head_to_head
            elif self._snakeHasLostHeadToHead(snake):
                collisions.append(snake)

        # Kill snakes that collided
        for snake in collisions:
            self.snake.health = 0

    def _snakeIsOutOfBounds(self, snake: SimpleSnake):
        x = snake.body[0][0]
        y = snake.body[0][1]
        return not 0 <= x < self.width or not 0 <= y < self.height

    def _snakeHasBodyCollided(self, snake: SimpleSnake):
        x = snake.body[0][0]
        y = snake.body[0][1]
        for snake in self.snakes:
            # Ignore heads, we'll check that in other places
            for segment in snake.body[1:]:
                if x == segment[0] and y == segment[1]:
                    return True
        return False

    def _snakeHasLostHeadToHead(self, snake: SimpleSnake):
        for other_snake in self.snakes:
            if other_snake == snake:
                continue
            if snake.body[0] == other_snake.body[0] and len(
                    other_snake.body) >= len(snake.body):
                return True
        return False


class TurnBuilder:

    def __init__(self, board: BoardState, moves: Tuple[models.Direction]):
        self.board = board
        self.moves = moves

    def do_move(self, snk_id: int, d: models.Direction) -> 'TurnBuilder':
        assert (self.board.turn < self.board.max_depth,
                'Cannot call do_move when simulation is at max depth.')
        assert (snk_id == len(self.moves), 'Must declare snake moves in order')
        assert (snk_id >= 0 and
                snk_id < len(self.board.snakes), 'Snake id must be in range')
        assert ((self.board.snakes[snk_id].health != 0 and d is not None) or
                (self.board.snakes[snk_id].health == 0 and d is None),
                'Dead snakes move None')
        return TurnBuilder(self.board, tuple((*self.moves, d)))

    def do_turn(self) -> BoardState:
        return self.board.do_turn(self.moves)
