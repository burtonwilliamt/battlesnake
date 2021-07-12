import random
import math
from typing import List
from enum import Enum

import cherrypy

import models
from snakes.default import BattlesnakeServer


def valid_moves(data:models.Data, snk:models.Battlesnake) -> List[models.Move]:
    return [mv for mv in models.Move.CARDINAL_FOUR() if data.board.can_move(snk, mv)]


class Plan:
    def __init__(self):
        steps = []
        self.next_step = 0
        pass

    def next(self, ) -> models.Move:
        mv = self.steps[self.next_step]
        self.next_step += 1
        if self.next_step >= len(self.steps):
            self.next_step = 0
        return mv


# Move right
# If you can't move down(or are full and need food), move right repeat.
# If you can't move left, move down, repeat
# If you can't move up, move right

class LoopMode(Enum):
    right = 0
    down = 1
    left = 2
    up = 3
    priming = 4


class InvLoopPlan(Plan):
    def __init__(self, left_column:int):
        self.left_column = left_column
        self.mode = LoopMode.priming

    def top_food(self, data:models.Data) -> models.Coord:
        board = data.board
        for y in range(board.height):
            for dx in (0, 1):
                if board.grid[self.left_column+dx][y] == models.Tile.FOOD:
                    return models.Coord.from_x_y(self.left_column+dx, y)
        return None

    def needs_right_bump(self, data) -> bool:
        snk = data.you
        is_full_column = snk.length >= 2*data.board.height-1
        if not is_full_column:
            return False
        flat_side = math.ceil(snk.length/2)%data.board.height == 0
        half_out = math.ceil(snk.length/2)%data.board.height == 2
        return flat_side or half_out


    def next(self, data:models.Data) -> models.Move:
        snk = data.you
        board = data.board
        if self.mode == LoopMode.priming:
            if snk.head.x > self.left_column:
                return models.Move.LEFT()
            elif snk.head.x < self.left_column:
                return models.Move.RIGHT()
            elif snk.head.y > 1:
                return models.Move.DOWN()
            elif snk.head.y == 1:
                self.mode = LoopMode.right
                return models.Move.DOWN()
        if self.mode == LoopMode.right:
            print('mode right')
            if self.needs_right_bump(data) and snk.health < snk.length + 2:
                return models.Move.RIGHT()
            if board.can_move(snk, models.Move.UP()):
                self.mode = LoopMode.up
                return models.Move.UP()
            else:
                return models.Move.RIGHT()
        elif self.mode == LoopMode.up:
            print('mode up')
            # If we can get food to our left, do so
            if board.get(snk.head.x-1, snk.head.y) == models.Tile.FOOD:
                self.mode = LoopMode.down
                return models.Move.LEFT()
            # If we're hungry and can move up, do so
            food = self.top_food(data)
            if food is not None:
                distance = abs(snk.head.x-food.x) + abs(snk.head.y-food.y)
                loop_size = max(snk.length+2, 2*(snk.head.y+1))
                if snk.health < loop_size + distance:
                    return models.Move.UP()
            # If we're not hungry and we can move left, do so
            if board.can_move(snk, models.Move.LEFT()):
                self.mode = LoopMode.down
                return models.Move.LEFT()
            # Else move up
            else:
                return models.Move.UP()
        elif self.mode == LoopMode.down:
            print('mode down')
            if board.can_move(snk, models.Move.DOWN()):
                return models.Move.DOWN()
            elif board.can_move(snk, models.Move.RIGHT()):
                self.mode = LoopMode.up
                return models.Move.RIGHT()
            elif board.can_move(snk, models.Move.LEFT()):
                self.mode = LoopMode.up
                return models.Move.LEFT()
            else: # happens when we aren't quite one column over yet
                self.mode = LoopMode.up
                return models.Move.UP()


class LoopPlan(Plan):
    def __init__(self, left_column:int):
        self.left_column = left_column
        self.mode = LoopMode.priming

    def top_food(self, data:models.Data) -> models.Coord:
        board = data.board
        # data.you.length has to be strictly greater than a saturated column
        meta_column = math.floor((data.you.length-1)/(2*data.board.height))
        print(f'meta column: {meta_column}')
        for y in range(board.height-1, -1, -1):
            for dx in (0, 1):
                x = self.left_column+meta_column*2+dx
                if board.grid[x][y] == models.Tile.FOOD:
                    return models.Coord.from_x_y(x, y)
        return None

    def needs_right_bump(self, data) -> bool:
        snk = data.you
        is_full_column = snk.length >= 2*data.board.height-1
        if not is_full_column:
            print('Not full column')
            return False
        flat_side = math.ceil(snk.length/2)%data.board.height == 0
        half_out = math.ceil(snk.length/2)%data.board.height == 1
        print(f'flat: {flat_side} half: {half_out}')
        return flat_side or half_out


    # If you can't move down(or are full and need food), move right repeat.
    # If you can't move left, move down, repeat
    # If you can't move up, move right
    def next(self, data:models.Data) -> models.Move:
        snk = data.you
        board = data.board
        if self.mode == LoopMode.priming:
            if snk.head.x > self.left_column:
                return models.Move.LEFT()
            elif snk.head.x < self.left_column:
                return models.Move.RIGHT()
            elif snk.head.y < data.board.height-2:
                return models.Move.UP()
            elif snk.head.y == data.board.height-2:
                self.mode = LoopMode.right
                return models.Move.UP()
        if self.mode == LoopMode.right:
            print('mode right')
            if self.needs_right_bump(data) and snk.health < snk.length+2:
                return models.Move.RIGHT()
            if board.can_move(snk, models.Move.DOWN()):
                self.mode = LoopMode.down
                return models.Move.DOWN()
            else:
                return models.Move.RIGHT()
        elif self.mode == LoopMode.down:
            print('mode down')
            # If we can get food to our left, do so
            if board.get(snk.head.x-1, snk.head.y) == models.Tile.FOOD:
                self.mode = LoopMode.up
                return models.Move.LEFT()
            # If we're hungry and can move down, do so
            food = self.top_food(data)
            if food is not None:
                print(f'Found food at {food.x},{food.y}')
                distance = abs(snk.head.x-food.x) + abs(snk.head.y-food.y)
                loop_size = max(snk.length+2, 2*(data.board.height-snk.head.y))
                if snk.health < loop_size + distance and board.can_move(snk, models.Move.DOWN()):
                    return models.Move.DOWN()
            else:
                print('No food')
            # If we're not hungry and we can move left, do so
            if board.can_move(snk, models.Move.LEFT()):
                self.mode = LoopMode.up
                return models.Move.LEFT()
            else:
                return models.Move.DOWN()

        elif self.mode == LoopMode.up:
            print('mode up')
            if board.can_move(snk, models.Move.UP()):
                return models.Move.UP()
            elif board.can_move(snk, models.Move.RIGHT()):
                self.mode = LoopMode.right
                return models.Move.RIGHT()
            elif board.can_move(snk, models.Move.LEFT()):
                self.mode = LoopMode.down
                return models.Move.LEFT()
            else: # happens when we aren't quite one column over yet
                self.mode = LoopMode.down
                return models.Move.DOWN()



class SmartSnake:
    def __init__(self, data:models.Data):
        pass

    def move(self, data:models.Data) -> models.Move:
        pass


class Looper(SmartSnake):
    def __init__(self, data:models.Data, left_column:int=0):
        self.plan = LoopPlan(left_column)

    def move(self, data:models.Data) -> models.Move:
        return self.plan.next(data)


class InvLooper(SmartSnake):
    def __init__(self, data:models.Data, left_column:int=0):
        self.plan = InvLoopPlan(left_column)

    def move(self, data:models.Data) -> models.Move:
        return self.plan.next(data)


class Medusa(BattlesnakeServer):
    def __init__(self):
        self.smart_snakes = {} #smart_snakes[game_id][snake_id] = snake


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # Go here for options: https://play.battlesnake.com/references/customizations/
        return {
            'apiversion': '1',
            'author': 'drzoid',
            'color': '#8101bc',
            'head': 'safe',
            'tail': 'freckled',
            'version': '1.0.0',
        }

    def get_col_for_snake(self, snakes:List[models.Battlesnake], snake_id:str, width:int):
        snake = None
        left_to_right = list(snakes)
        left_to_right.sort(key=lambda snk: snk.head.x)
        for i, snk in enumerate(left_to_right):
            if snk.id == snake_id:
                return width*i
        raise ValueError('Could not find snake with snake_id')

    def split_snakes(self, data:models.Data, width:int):
        max_per_side = math.floor(data.board.width/width)
        need_bottom =  max_per_side < len(data.board.snakes)
        if not need_bottom:
            return list(data.board.snakes), []
        else:
            bottom_to_top = list(data.board.snakes)
            bottom_to_top.sort(key=lambda snk: snk.head.y)
            top = bottom_to_top[-max_per_side::]
            bottom = bottom_to_top[0:len(bottom_to_top)-len(top)]
            return top, bottom

    def get_snake_zone(self, data:models.Data, snake_id:str, width:int):
        top_snakes, bottom_snakes = self.split_snakes(data, width)
        snake_group = top_snakes
        is_top = True
        for snake in bottom_snakes:
            if snake.id == snake_id:
                snake_group = bottom_snakes
                is_top = False
        col = self.get_col_for_snake(snake_group, snake_id, width)
        return is_top, col

    def get_or_make_smart_snake(self, data:models.Data, snake_id:int):
        game_id = data.game.id
        if game_id not in self.smart_snakes:
            self.smart_snakes[game_id] = {}
        if snake_id not in self.smart_snakes[game_id]:
            print('Made new smart snake')
            is_top, col = self.get_snake_zone(data, snake_id, 2)
            runner = None
            if is_top:
                runner = Looper(data, col)
            else:
                runner = InvLooper(data, col)
            self.smart_snakes[game_id][snake_id] = runner
        return self.smart_snakes[game_id][snake_id]

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        data = models.Data(cherrypy.request.json)

        snake = self.get_or_make_smart_snake(data, data.you.id)

        print('START')
        print(f'Timeout: {data.game.timeout}ms')

        return 'ok'

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = models.Data(cherrypy.request.json)

        snake = self.get_or_make_smart_snake(data, data.you.id)
        move = snake.move(data)

        print(f'MOVE: {move.name}')
        return move.json()

