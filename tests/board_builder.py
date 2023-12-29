from typing import List, Mapping, Tuple

import src.models as models


class BoardBuilder:
    # {letter} is the head of snake with that name
    #   if letter is capital, that means tail has extra segment
    # <|^|v|> is the body. Arrow points towards head
    # * is food

    EXAMPLE_BOARD = """
    v......
    va<....
    >>^....
    ....*..
    .*.....
    ..v>>b.
    .......
    """

    FOOD = "*"
    RIGHT = ">"
    LEFT = "<"
    UP = "^"
    DOWN = "v"
    HEADS = set(["a", "b", "c", "d"])

    def __init__(self, board_str: str, healths: Mapping[str, int]):
        self.grid = self.str_to_grid(board_str)
        self.healths = healths

    @classmethod
    def str_to_grid(cls, board_str: str) -> List[List[str]]:
        rows = [ln.strip() for ln in board_str.splitlines() if len(ln.strip()) > 0]

        height = len(rows)
        width = len(rows[0])
        for row in rows:
            if len(row) != width:
                print(f"expected {width} but got {len(row)}")
                raise ValueError("All rows must be the same width.")

        # We want rows[0] to be bottom line
        rows.reverse()

        # rows is in [y][x] format, we need to switch that to [x][y]
        res = [[None for _ in range(height)] for _ in range(width)]
        for x in range(width):
            for y in range(height):
                res[x][y] = rows[y][x]

        return res

    def grid_iter(self) -> Tuple[models.Coord, str]:
        for x, col in enumerate(self.grid):
            for y, val in enumerate(col):
                yield (models.Coord({"x": x, "y": y}), val)

    def find_food(self) -> List[Mapping[str, int]]:
        return [coord.json() for coord, val in self.grid_iter() if val == self.FOOD]

    def find_heads(self) -> List[models.Coord]:
        locations = []
        heads = set()
        for coord, val in self.grid_iter():
            if val.lower() not in self.HEADS:
                continue
            if val in heads:
                raise AssertionError("Cannot have duplicate heads in board.")
            heads.add(val.lower())
            locations.append(coord)
        return sorted(locations, key=lambda coord: self.grid[coord.x][coord.y].lower())

    def safe_get(self, x: int, y: int) -> str:
        if len(self.grid) > x >= 0 and len(self.grid[x]) > y >= 0:
            return self.grid[x][y]
        return None

    def find_previous(self, coord: models.Coord) -> models.Coord:
        # If tile points to our current pos then it's the previous segment
        x = coord.x
        y = coord.y
        if self.safe_get(x + 1, y) == self.LEFT:
            return models.Coord.from_x_y(x + 1, y)
        elif self.safe_get(x - 1, y) == self.RIGHT:
            return models.Coord.from_x_y(x - 1, y)
        elif self.safe_get(x, y + 1) == self.DOWN:
            return models.Coord.from_x_y(x, y + 1)
        elif self.safe_get(x, y - 1) == self.UP:
            return models.Coord.from_x_y(x, y - 1)
        else:
            return None

    def find_snakes(self) -> List[dict]:
        snakes = []
        heads = self.find_heads()
        for i, head in enumerate(heads):
            head_val = self.grid[head.x][head.y]

            # Trace the body
            body = []
            segment = head
            while segment:
                body.append(segment.json())
                segment = self.find_previous(segment)
            # If the head is uppercase, add an extra tail segment
            if not head_val.islower():
                body.append(body[-1])

            name = head_val.lower()
            snk = {
                "id": name + "_id",
                "name": name,
                "health": self.healths[name],
                "body": body,
                "latency": 0,
                "head": body[0],
                "length": len(body),
                "shout": "",
                "squad": "",
            }
            snakes.append(snk)
        return snakes

    def to_board(self) -> models.Board:
        return models.Board(
            {
                "width": len(self.grid),
                "height": len(self.grid[0]),
                "food": self.find_food(),
                "snakes": self.find_snakes(),
                "hazards": [],
            }
        )
