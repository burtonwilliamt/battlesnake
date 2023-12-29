import unittest
from typing import Iterable, Sequence

from tests.board_builder import BoardBuilder
import src.models as models


class TestBoardBuilder(unittest.TestCase):
    def test_str_to_grid(self):
        self.assertEqual(
            BoardBuilder.str_to_grid(
                """
        a...
        .b..
        ..c.
        ...d
        """
            ),
            [
                [".", ".", ".", "a"],
                [".", ".", "b", "."],
                [".", "c", ".", "."],
                ["d", ".", ".", "."],
            ],
        )

    def test_grid_iter(self):
        bb = BoardBuilder(
            """
            v....vv
            va<..Cv
            >>^...d
            ....*..
            .*.....
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 0,
                "d": 42,
            },
        )
        coords = set()
        for coord, val in bb.grid_iter():
            x = coord.x
            y = coord.y
            self.assertEqual(
                val,
                bb.grid[x][y],
                "grid_iter returned the wrong value for this coordinate",
            )
            coords.add((x, y))
        self.assertEqual(
            len(coords),
            len(bb.grid) * len(bb.grid[0]),
            "grid_iter did not return everything exactly once",
        )

    def test_to_board(self):
        b = BoardBuilder(
            """
            v....vv
            va<..Cv
            >>^...d
            ....*..
            .*.....
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 0,
                "d": 42,
            },
        ).to_board()
        self.assertEqual(b.width, 7)
        self.assertEqual(b.height, 6)
        self.assertEqual(len(b.hazards), 0)

        def to_coords(*args):
            return [models.Coord.from_x_y(arg[0], arg[1]) for arg in args]

        self.assertCountEqual(b.food, to_coords((1, 1), (4, 2)))

        self.assertEqual(len(b.snakes), 4)
        snks = {}
        for snk in b.snakes:
            snks[snk.name] = snk

        def check_snake(
            snk: models.Battlesnake,
            *,
            id_str: str,
            health: int,
            length: int,
            body: Iterable[Sequence]
        ):
            self.assertEqual(snk.id, id_str)
            self.assertEqual(snk.health, health)
            self.assertEqual(snk.length, length)
            self.assertSequenceEqual(
                snk.body,
                to_coords(*body),
            )

        check_snake(
            snks["a"],
            id_str="a_id",
            health=51,
            length=7,
            body=((1, 4), (2, 4), (2, 3), (1, 3), (0, 3), (0, 4), (0, 5)),
        )

        check_snake(
            snks["b"],
            id_str="b_id",
            health=100,
            length=3,
            body=((5, 0), (4, 0), (3, 0)),
        )

        check_snake(
            snks["c"],
            id_str="c_id",
            health=0,
            length=3,
            body=((5, 4), (5, 5), (5, 5)),
        )

        check_snake(
            snks["d"],
            id_str="d_id",
            health=42,
            length=3,
            body=((6, 3), (6, 4), (6, 5)),
        )

    def test_snakes_in_name_order(self):
        bb = BoardBuilder(
            """
            v....vv
            va<..Cv
            >>^...d
            ....*..
            .*.....
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 0,
                "d": 42,
            },
        )

        self.assertEqual(
            bb.find_heads(),
            [
                models.Coord.from_x_y(1, 4),
                models.Coord.from_x_y(5, 0),
                models.Coord.from_x_y(5, 4),
                models.Coord.from_x_y(6, 3),
            ],
            "Heads should be returned in alphabetical order by name.",
        )

        b = bb.to_board()
        self.assertEqual(
            [snk.name for snk in b.snakes],
            ["a", "b", "c", "d"],
            "BoardBuilder should order the snakes by their name.",
        )
