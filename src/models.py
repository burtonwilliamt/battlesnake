from typing import List
from enum import Enum
from dataclasses import dataclass


class BattlesnakeInfo:
    # Go here for options: https://play.battlesnake.com/references/customizations/
    def __init__(
        self,
        *,
        author: str = "unowned",
        color: str = "#606060",
        head: str = "default",
        tail: str = "default",
        version: str = None,
    ):
        self.author = author
        self.color = color
        self.head = head
        self.tail = tail
        self.version = version

    def json(self):
        resp = {
            "apiversion": "1",
            "author": self.author,
            "color": self.color,
            "head": self.head,
            "tail": self.tail,
        }

        if self.version is not None:
            resp["version"] = self.version

        return resp


class Coord:
    def __init__(self, data: dict):
        self.x = data["x"]
        self.y = data["y"]

    def __eq__(self, other):
        if not isinstance(other, Coord):
            return False
        return other.x == self.x and other.y == self.y

    def __repr__(self):
        return f"<Coord({self.x}, {self.y})>"

    @classmethod
    def from_x_y(cls, x: int, y: int):
        return cls({"x": x, "y": y})

    def json(self):
        return {"x": self.x, "y": self.y}


class Tile(Enum):
    OUTSIDE = 0
    SNAKE = 1
    HAZARD = 2
    POTENTIAL_SNAKE = 3
    FOOD = 4
    EMPTY = 5


class Direction:
    def __init__(self, name: str, rel_x: int, rel_y: int):
        self.name = name
        self.rel_x = rel_x
        self.rel_y = rel_y

    def __repr__(self):
        return f"<Direction:{self.name}>"


UP = Direction("up", 0, 1)
DOWN = Direction("down", 0, -1)
LEFT = Direction("left", -1, 0)
RIGHT = Direction("right", 1, 0)

CARDINAL_FOUR = [UP, DOWN, LEFT, RIGHT]


class Move:
    def __init__(self, direction: Direction, shout: str = None):
        self.direction = direction
        self.shout = "" if shout is None else shout

    def __repr__(self):
        if self.shout is None:
            return f"<Move direction:{self.direction}>"
        else:
            return f"<Move direction:{self.direction} shout:{repr(self.shout)}>"

    def json(self):
        return {"move": self.direction.name, "shout": self.shout}


class Battlesnake:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.health = data["health"]
        self.body = [Coord(pt) for pt in data["body"]]
        self.latency = float(data["latency"]) if data["latency"] != "" else None
        self.head = Coord(data["head"])
        self.length = data["length"]
        self.shout = data["shout"] if "shout" in data else None
        self.squad = data["squad"] if "squad" in data else None


class Board:
    def __init__(self, data: dict):
        # data fields
        self.height = data["height"]
        self.width = data["width"]
        self.food = [Coord(pt) for pt in data["food"]]
        self.hazards = [Coord(pt) for pt in data["hazards"]]
        self.snakes = [Battlesnake(snk) for snk in data["snakes"]]

        # custom fields
        self.grid = [
            [Tile.EMPTY for _ in range(self.height)] for _ in range(self.width)
        ]
        for fd in self.food:
            self.grid[fd.x][fd.y] = Tile.FOOD

        for hzd in self.hazards:
            self.grid[hzd.x][hzd.y] = Tile.HAZARD

        for snk in self.snakes:
            for segment in snk.body:
                self.grid[segment.x][segment.y] = Tile.SNAKE

    def get(self, x: int, y: int) -> Tile:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return Tile.OUTSIDE
        else:
            return self.grid[x][y]

    def can_move(self, snk: Battlesnake, d: Direction) -> bool:
        x = snk.head.x + d.rel_x
        y = snk.head.y + d.rel_y
        is_clear = self.get(x, y) in (Tile.EMPTY, Tile.FOOD)
        is_my_tail = snk.body[-1].x == x and snk.body[-1].y == y
        return is_clear or is_my_tail

    def can_safe_move(self, snk: Battlesnake, d: Direction) -> bool:
        x = snk.head.x + d.rel_x
        y = snk.head.y + d.rel_y
        return self.get(x, y) in (Tile.EMPTY, Tile.FOOD)


class Ruleset:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.version = data["version"]


class Game:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.ruleset = Ruleset(data["ruleset"])
        self.timeout = float(data["timeout"])


class Data:
    def __init__(self, data: dict):
        self.game = Game(data["game"])
        self.turn = data["turn"]
        self.board = Board(data["board"])
        self.you = Battlesnake(data["you"])
