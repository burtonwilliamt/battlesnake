import src.models as models
from src.planning.temporal_body import TemporalBody

MAX_HEALTH = 100

class Simulation:

    def __init__(self, board: models.Board, max_depth=100):
        self.turn = 0
        self.max_depth = max_depth

        # Simplify the ids to 0...n-1 for array access
        live_snakes = [snk for snk in board.snakes if snk.health > 0]
        self.simple_ids = {}
        for i, snk in enumerate(live_snakes):
            self.simple_ids[snk.id] = i
        self.snake_ids = list(range(len(live_snakes)))

        # bodies that keep track of history
        self.bodies = [TemporalBody(snk.body) for snk in live_snakes]

        # tables where each row is one turn, column is that snake's value
        num_snakes = len(live_snakes)
        # First row is starting health
        self.t_health = [[snk.health for snk in live_snakes]
                        ] + [[None] * num_snakes] * self.max_depth - 1

        # self.t_move_choices[t] are choices received on turn t
        # when these choices are applied, it becomes turn t+1
        self.t_move_choices = [[None] * num_snakes] * self.max_depth

        # List of food that's available
        self.t_food = [list(board.food)
                      ] + [list() for _ in range(self.max_depth - 1)]

        # List of snakes that grew at the start of turn i
        self.t_grown_snakes = [list() for _ in range(self.max_depth)]

        # 2d array of board state
        #self.queue_grid = []
        #for i in range(board.width):
        #self.queue_grid.append([])
        #for j in range(board.height):
        #self.queue_grid[i].append(queue.deque())
        #self.queue_grid[i][j].append(board.get(i, j))

    def do_move(self, snk_id: int, d: models.Direction):
        self.t_move_choices[self.turn][snk_id] = d

    def undo_move(self, snk_id: int):
        self.t_move_choices[self.turn][snk_id] = None

    def do_turn(self):
        self.moveSnakes()
        self.reduceSnakeHealth()
        self.maybeFeedSnakes()
        #self.maybeSpawnFood()
        self.maybeEliminateSnakes()
        self.turn += 1

    def undo_turn(self):
        self.turn -= 1
        self.undo_maybeEliminateSnakes()
        #self.undo_maybeSpawnFood()
        self.undo_maybeFeedSnakes()
        self.undo_reduceSnakeHealth()
        self.undo_moveSnakes()

    def snake_is_dead(self, snk_id):
        return self.t_health[self.turn][snk_id] <= 0

    def moveSnakes(self):
        for snk_id in self.snake_ids:
            if self.snake_is_dead(snk_id):
                continue
            body = self.bodies[snk_id]
            d = self.t_move_choices[self.turn][snk_id]
            new_head = models.Coord()
            new_head.x = body.head().x + d.rel_x
            new_head.y = body.head().y + d.rel_y
            body.add_head(new_head)
            body.del_tail

    def undo_moveSnakes(self):
        for snk_id in self.snake_ids:
            if self.snake_is_dead(snk_id):
                continue
            body = self.bodies[snk_id]
            body.del_head()
            body.undel_tail()

    def reduceSnakeHealth(self):
        for snk_id in self.snake_ids:
            if not self.snake_is_dead(snk_id):
                old_health = self.t_health[self.turn][snk_id]
                self.t_health[self.turn + 1][snk_id] = old_health - 1

    def undo_reduceSnakeHealth(self):
        for snk_id in self.snake_ids:
            self.t_health[self.turn + 1][snk_id] = None

    def maybeFeedSnakes(self):
        for food in self.t_food[self.turn]:
            food_eaten = False
            for snk_id in self.snake_ids:
                # Dead snakes can't eat
                if self.snake_is_dead(snk_id):
                    continue
                body = self.bodies[snk_id]
                if body.head().x == food.x and body.head().y == food.y:
                    food_eaten = True
                    self.t_health[self.turn + 1][snk_id] = MAX_HEALTH
                    body.grow()
                    self.t_grown_snakes[self.turn + 1].append(snk_id)
            if not food_eaten:
                self.t_food[self.turn + 1].append(food)
            else:
                self.t_eaten_food[self.turn + 1].append(food)

    def undo_maybeFeedSnakes(self):
        # any snakes that grew should un-grow
        for snk_id in self.t_grown_snakes[self.turn + 1]:
            self.bodies[snk_id].undo_grow()
        self.t_grown_snakes[self.turn + 1].clear()
        # clear the food array
        self.t_food[self.turn + 1].clear()

    def maybeEliminateSnakes(self):
        pass

    def undo_maybeEliminateSnakes(self):
        pass

