import unittest
from typing import List, Tuple, Set

from src.planning.simulation import Simulation
import src.models as models

# Board Encoding 1:

# F_ food
# B* body
#   BL body, continues left
#   BR body, continues right
#   BU body, continues up
#   BD body, continues down
# H_ head
# T* tail
#   T1 tail one deep
#   T2 tail two deep
#   ...

# Board Encoding 2:
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

FOOD = '*'
RIGHT = '>'
LEFT = '<'
UP = '^'
DOWN = 'v'
HEADS = set('a', 'b', 'c', 'd')


def str_to_grid(board: str) -> List[List[str]]:
    rows = [ln for ln in board.splitlines()]

    height = len(rows)
    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            raise ValueError('All rows must be the same width.')

    # We want rows[0] to be bottom line
    rows.reverse()

    # rows is in [y][x] format, we need to switch that to [x][y]
    res = [[None for _ in range(height)] for _ in range(width)]
    for x in range(width):
        for y in range(height):
            res[x][y] = rows[y][x]

    return res


def grid_iter(grid: List[List[str]]) -> Tuple[models.Coord, str]:
    for x, col in enumerate(grid):
        for y, val in enumerate(col):
            yield (models.Coord({'x': x, 'y': y}), val)


def find_food(grid: List[List[str]]) -> List[models.Coord]:
    return [coord.json() for coord, val in grid_iter(grid) if val == FOOD]


def find_heads(grid: List[List[str]]) -> List[models.Coord]:
    return [
        coord.json() for coord, val in grid_iter(grid) if val.lower() in HEADS
    ]


def safe_get(grid: List[List[str]], x: int, y: int) -> str:
    if len(grid) > x >= 0 and len(grid[x]) > y >= 0:
        return grid[x][y]
    return None


def find_previous(grid: List[List[str]], coord: models.Coord) -> models.Coord:
    # If tile points to our current pos then it's the previous segment
    x = coord.x
    y = coord.y
    if safe_get(grid, x + 1, y) == LEFT:
        return (x + 1, y)
    elif safe_get(grid, x - 1, y) == RIGHT:
        return (x - 1, y)
    elif safe_get(grid, x, y + 1) == DOWN:
        return (x, y + 1)
    elif safe_get(grid, x, y - 1) == UP:
        return (x, y - 1)
    else:
        return None


#TODO: finish this
def find_snakes(grid: List[List[str]]) -> List[models.Battlesnake]:
    snakes = []
    heads = find_heads(grid)
    for i, head in enumerate(heads):
        body = []
        segment = head
        while segment:
            body.append(segment)
            segment = find_previous(grid, segment[0], segment[1])
    return snakes


def str_to_board(in_str: str) -> models.Board:
    grid = str_to_grid(in_str.strip())
    return models.Board({
        'width': len(grid),
        'height': len(grid[0]),
        'food': find_food(grid),
        'snakes': find_snakes(grid),
        'hazards': [],
    })


class TestSimulation(unittest.TestCase):

    def test_init(self):
        pass
