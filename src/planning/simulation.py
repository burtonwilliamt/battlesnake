from typing import Iterable, Mapping

import src.models as models
from src.planning.temporal_body import TemporalBody

MAX_HEALTH = 100


class Simulation:
    """Simulate a game of BattleSnake

    Attributes:
    turn
    max_depth
    simple_ids
    snake_ids
    names
    width
    height

    Volatile attributes:
    bodies
    healths
    food

    """

    def __init__(self, board: models.Board, max_depth=100):
        self.turn = 0
        # NOTE: max_depth is the maximum turn number
        # This means that with max_depth, turn 0 is the only valid turn.
        # Calling do_move or do_turn when turn == max_depth will error.
        # The arrays should be size max_depth+1 to initialize turn 0 correctly.
        self.max_depth = max_depth
        self.width = board.width
        self.height = board.height

        # Simplify the ids to 0...n-1 for array access
        live_snakes = [snk for snk in board.snakes if snk.health > 0]
        self.simple_ids = {}
        for i, snk in enumerate(live_snakes):
            self.simple_ids[snk.id] = i
        self.snake_ids = list(range(len(live_snakes)))
        self.names = [snk.name for snk in live_snakes]

        # bodies that keep track of history
        self.bodies = [TemporalBody(snk.body) for snk in live_snakes]

        # tables where each row is one turn, column is that snake's value
        num_snakes = len(live_snakes)
        # First row is starting health
        self._t_health = [[
            snk.health for snk in live_snakes
        ]] + [[None] * num_snakes for _ in range(self.max_depth)]

        # self._t_move_choices[t] are choices received on turn t
        # when these choices are applied, it becomes turn t+1
        self._t_move_choices = [
            [None] * num_snakes for _ in range(self.max_depth + 1)
        ]

        # List of food that's available
        self._t_food = [list(board.food)] + [[] for _ in range(self.max_depth)]

        # List of snakes that grew at the start of turn i
        self._t_grown_snakes = [[] for _ in range(self.max_depth + 1)]

        # 2d array of board state
        #self.queue_grid = []
        #for i in range(board.width):
        #self.queue_grid.append([])
        #for j in range(board.height):
        #self.queue_grid[i].append(queue.deque())
        #self.queue_grid[i][j].append(board.get(i, j))

    @property
    def healths(self) -> Mapping[int, int]:
        return self._t_health[self.turn]

    @property
    def food(self) -> Iterable[models.Coord]:
        return self._t_food[self.turn]

    def turns_alive(self, snk_id:int) -> int:
        """How long a snake has lived for. If still alive this is self.turn"""
        for i in range(self.turn, -1, -1):
            if self._t_health[i][snk_id] > 0:
                return i
        return 0

    def do_move(self, snk_id: int, d: models.Direction):
        if self.turn == self.max_depth:
            raise AssertionError(
                'Cannot call do_move when simulation is at max depth.')
        self._t_move_choices[self.turn][snk_id] = d

    def undo_move(self, snk_id: int):
        self._t_move_choices[self.turn][snk_id] = None

    def do_turn(self):
        if self.turn == self.max_depth:
            raise AssertionError(
                'Cannot call do_turn when simulation is at max depth.')
        self._moveSnakes()
        self._reduceSnakeHealth()
        self._maybeFeedSnakes()
        #self._maybeSpawnFood()
        self._maybeEliminateSnakes()
        self.turn += 1

    def undo_turn(self):
        if self.turn == 0:
            raise AssertionError('Cannot undo beyond the start of simulation.')
        self.turn -= 1
        self._undo_maybeEliminateSnakes()
        #self._undo_maybeSpawnFood()
        self._undo_maybeFeedSnakes()
        self._undo_reduceSnakeHealth()
        self._undo_moveSnakes()

    def snake_is_dead(self, snk_id):
        return self._t_health[self.turn][snk_id] <= 0

    def _moveSnakes(self):
        for snk_id in self.snake_ids:
            # Skip dead snakes
            if self.snake_is_dead(snk_id):
                continue

            # Raise error if no move was submitted
            if self._t_move_choices[self.turn][snk_id] is None:
                raise ValueError(f'Snake {snk_id} did not submit a move.')

            d = self._t_move_choices[self.turn][snk_id]
            body = self.bodies[snk_id]
            new_head = models.Coord({
                'x': body.head().x + d.rel_x,
                'y': body.head().y + d.rel_y,
            })
            body.add_head(new_head)
            body.del_tail()

    def _undo_moveSnakes(self):
        for snk_id in self.snake_ids:
            if self.snake_is_dead(snk_id):
                continue
            body = self.bodies[snk_id]
            body.undo_add_head()
            body.undo_del_tail()

    def _reduceSnakeHealth(self):
        for snk_id in self.snake_ids:
            old_health = self._t_health[self.turn][snk_id]
            if self.snake_is_dead(snk_id):
                self._t_health[self.turn + 1][snk_id] = old_health
            else:
                self._t_health[self.turn + 1][snk_id] = old_health - 1

    def _undo_reduceSnakeHealth(self):
        for snk_id in self.snake_ids:
            self._t_health[self.turn + 1][snk_id] = None

    def _maybeFeedSnakes(self):
        for food in self._t_food[self.turn]:
            food_eaten = False
            for snk_id in self.snake_ids:
                # Dead snakes can't eat
                if self.snake_is_dead(snk_id):
                    continue
                body = self.bodies[snk_id]
                if body.head().x == food.x and body.head().y == food.y:
                    food_eaten = True
                    self._t_health[self.turn + 1][snk_id] = MAX_HEALTH
                    body.grow()
                    self._t_grown_snakes[self.turn + 1].append(snk_id)
            if not food_eaten:
                self._t_food[self.turn + 1].append(food)

    def _undo_maybeFeedSnakes(self):
        # any snakes that grew should un-grow
        for snk_id in self._t_grown_snakes[self.turn + 1]:
            self.bodies[snk_id].undo_grow()
        self._t_grown_snakes[self.turn + 1].clear()
        # clear the food array
        self._t_food[self.turn + 1].clear()

    def _maybeEliminateSnakes(self):
        # Snakes that starve or go out of bounds die first
        for snk_id in self.snake_ids:
            # Skip already eliminated snakes
            if self._snakeIsOutOfHealth(snk_id):
                continue
            # Check for bounds
            elif self._snakeIsOutOfBounds(snk_id):
                self._t_health[self.turn + 1][snk_id] = 0

        # All remaining eliminations happen simultaneously
        # This is so that eliminated snakes cause others to be eliminated
        collisions = []
        for snk_id in self.snake_ids:
            # Skip dead snakes
            if self._t_health[self.turn + 1][snk_id] == 0:
                continue
            # Check for body
            elif self._snakeHasBodyCollided(snk_id):
                collisions.append(snk_id)
            # Check for head_to_head
            elif self._snakeHasLostHeadToHead(snk_id):
                collisions.append(snk_id)

        # Kill snakes that collided
        for snk_id in collisions:
            self._t_health[self.turn + 1][snk_id] = 0

    def _snakeIsOutOfHealth(self, snk_id: int):
        return self._t_health[self.turn + 1][snk_id] == 0

    def _snakeIsOutOfBounds(self, snk_id: int):
        x = self.bodies[snk_id].head().x
        y = self.bodies[snk_id].head().y
        return not 0 <= x < self.width or not 0 <= y < self.height

    def _snakeHasBodyCollided(self, snk_id: int):
        x = self.bodies[snk_id].head().x
        y = self.bodies[snk_id].head().y
        for body in self.bodies:
            # Ignore heads, we'll check that in other places
            for segment in body.current_body[1:]:
                if x == segment.x and y == segment.y:
                    return True
        return False

    def _snakeHasLostHeadToHead(self, snk_id: int):
        this_body = self.bodies[snk_id]
        for other_id, body in enumerate(self.bodies):
            if other_id == snk_id:
                continue
            if body.head() == this_body.head() and len(body) >= len(this_body):
                return True
        return False

    def _undo_maybeEliminateSnakes(self):
        pass

    def render(self) -> str:
        grid = [['.' for _ in range(self.height)] for _ in range(self.width)]


        for f in self.food:
            grid[f.x][f.y] = '*'

        for snk_id, body in enumerate(self.bodies):
            # Don't render dead snakes
            if self.snake_is_dead(snk_id):
                continue

            name = self.names[snk_id]
            for i, segment in enumerate(body):
                # Handle the head
                if i == 0:
                    # If the tail is stacked, make it uppercase
                    if body.current_body[-1] == body.current_body[-2]:
                        grid[segment.x][segment.y] = name.upper()
                    else:
                        grid[segment.x][segment.y] = name.lower()
                    continue
                # Find one segment closer to the head
                newer = body.current_body[i-1]
                # Find the move required to get closer to the head
                to_head = (newer.x - segment.x, newer.y - segment.y)
                # If to_head is the direction to head, how to point
                if to_head == (1, 0):
                    grid[segment.x][segment.y] = '>'
                elif to_head == (-1, 0):
                    grid[segment.x][segment.y] = '<'
                elif to_head == (0, 1):
                    grid[segment.x][segment.y] = '^'
                elif to_head == (0, -1):
                    grid[segment.x][segment.y] = 'v'
                elif to_head == (0, 0):
                    pass
                else:
                    raise AssertionError('The segments aren\'t adjacent.')

        rows = []
        for y in reversed(range(self.height)):
            row = []
            for x in range(self.width):
                row.append(grid[x][y])
            rows.append(''.join(row))
        return '\n'.join(rows) + '\n'