from typing import List
from enum import Enum
from dataclasses import dataclass


class Coord:
    def __init__(self, data:dict):
        self.x = data['x']
        self.y = data['y']

    @classmethod
    def from_x_y(cls, x:int, y:int):
        return cls({'x':x, 'y':y})


class Tile(Enum):
    OUTSIDE = 0
    SNAKE = 1
    HAZARD = 2
    POTENTIAL_SNAKE = 3
    FOOD = 4
    EMPTY = 5


class Move:
    def __init__(self, name:str, rel_x:int, rel_y:int, shout:str=None):
        self.name = name
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.shout = '' if shout is None else shout

    def json(self):
        return {'move': self.name, 'shout': self.shout}

    @classmethod
    def UP(cls, shout:str=None) -> 'Move':
        return cls('up', 0, 1, shout)

    @classmethod
    def DOWN(cls, shout:str=None) -> 'Move':
        return cls('down', 0, -1, shout)

    @classmethod
    def LEFT(cls, shout:str=None) -> 'Move':
        return cls('left', -1, 0, shout)

    @classmethod
    def RIGHT(cls, shout:str=None) -> 'Move':
        return cls('right', 1, 0, shout)

    @classmethod
    def CARDINAL_FOUR(cls, shout:str=None) -> List['Move']:
        return [cls.UP(shout), cls.DOWN(shout), cls.LEFT(shout), cls.RIGHT(shout)]


class Battlesnake:
    def __init__(self, data:dict):
        self.id = data['id']
        self.name = data['name']
        self.health = data['health']
        self.body = [Coord(pt) for pt in data['body']]
        self.latency = data['latency']
        self.head = Coord(data['head'])
        self.length = data['length']
        self.shout = data['shout']
        self.squad = data['squad'] if 'squad' in data else None


class Board:
    def __init__(self, data:dict):
        # data fields
        self.height = data['height']
        self.width = data['width']
        self.food = [Coord(pt) for pt in data['food']]
        self.hazards = [Coord(pt) for pt in data['hazards']]
        self.snakes = [Battlesnake(snk) for snk in data['snakes']]

        # custom fields
        self.grid = [[Tile.EMPTY for _ in range(self.height)] for _ in range(self.width)]
        for fd in self.food:
            self.grid[fd.x][fd.y] = Tile.FOOD

        for hzd in self.hazards:
            self.grid[hzd.x][hzd.y] = Tile.HAZARD

        for snk in self.snakes:
            for segment in snk.body:
                self.grid[segment.x][segment.y] = Tile.SNAKE

    def get(self, x:int, y:int) -> Tile:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return Tile.OUTSIDE
        else:
            return self.grid[x][y]

    def can_move(self, snk:Battlesnake, move:Move) -> bool:
        x = snk.head.x+move.rel_x
        y = snk.head.y+move.rel_y
        is_clear = self.get(x, y) in (Tile.EMPTY, Tile.FOOD)
        is_my_tail = snk.body[-1].x == x and snk.body[-1].y == y
        return is_clear or is_my_tail

    def can_safe_move(self, snk:Battlesnake, move:Move) -> bool:
        x = snk.head.x+move.rel_x
        y = snk.head.y+move.rel_y
        return self.get(x, y) in (Tile.EMPTY, Tile.FOOD)


class Ruleset:
    def __init__(self, data:dict):
        self.name = data['name']
        self.version = data['version']


class Game:
    def __init__(self, data:dict):
        self.id = data['id']
        self.ruleset = Ruleset(data['ruleset'])
        self.timeout = data['timeout']


class Data:
    def __init__(self, data:dict):
        self.game = Game(data['game'])
        self.turn = data['turn']
        self.board = Board(data['board'])
        self.you = Battlesnake(data['you'])
