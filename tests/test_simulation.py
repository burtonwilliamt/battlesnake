import unittest
import textwrap
from typing import Mapping

from src.planning.simulation import Simulation
from tests.board_builder import BoardBuilder
import src.models as models


class TestSimulation(unittest.TestCase):
    def setUp(self):
        board = BoardBuilder(
            """
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        ).to_board()
        self.sim = Simulation(board)
        self.name_to_id = {}
        for i, name in enumerate(self.sim.names):
            self.name_to_id[name] = i

    def sim_to_str(self, sim: Simulation) -> str:
        grid = [["." for _ in range(sim.width)] for _ in range(sim.height)]

        # Place food
        for food in sim.food:
            grid[food.y][food.x] = "*"

        # Place snakes
        for snk_id, body in enumerate(sim.bodies):
            if sim.snake_is_dead(snk_id):
                continue

            # Place the head of the snake
            head = body.head()
            name = sim.names[snk_id]
            if name.lower() not in BoardBuilder.HEADS:
                raise ValueError("Snake has invalid testing name")
            # If two or more tail pieces stacked, uppercase the head
            if len(body) > 1 and body.current_body[-1] == body.current_body[-2]:
                grid[head.y][head.x] = name.upper()
            else:
                grid[head.y][head.x] = name.lower()

            # Place the rest of the snake
            previous = None
            for segment in body.current_body:
                if previous is not None:
                    delta = (previous.x - segment.x, previous.y - segment.y)
                    val = None
                    if delta == (1, 0):
                        val = ">"
                    elif delta == (-1, 0):
                        val = "<"
                    elif delta == (0, 1):
                        val = "^"
                    elif delta == (0, -1):
                        val = "v"
                    elif delta == (0, 0):
                        continue
                    else:
                        raise ValueError("Body segments aren't adjacent")
                    grid[segment.y][segment.x] = val
                previous = segment

        # Convert to string
        return "\n".join(["".join(row) for row in reversed(grid)])

    def expect_board(
        self,
        board_str: str,
        healths: Mapping[str, int],
    ):
        # Check that the board matches
        # Prevent having to escape the first line of board_str
        if board_str[0] == "\n":
            board_str = board_str[1:]
        actual = self.sim_to_str(self.sim).strip()
        expected = textwrap.dedent(board_str).strip()
        self.assertMultiLineEqual(
            actual,
            expected,
            "Simulation has wrong board state.\n"
            f"Actual:\n{actual}\n\nExpected:\n{expected}",
        )

        # Check the healths match
        self.assertEqual(
            len(self.sim.healths),
            len(healths),
            "Simulation has wrong number of healths",
        )
        for name, health in healths.items():
            self.assertEqual(
                self.sim.healths[self.name_to_id[name]],
                health,
                "Simulation health does not match expected.",
            )

    def test_init(self):
        self.expect_board(
            """
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        )

    def test_move(self):
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.RIGHT)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....*.
            ....>>b
            """,
            {
                "a": 50,
                "b": 99,
                "c": 1,
                "d": 41,
            },
        )

    def test_move_and_undo_move(self):
        # Do some move
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.RIGHT)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....*.
            ....>>b
            """,
            {
                "a": 50,
                "b": 99,
                "c": 1,
                "d": 41,
            },
        )

        # Roll it back partially
        self.sim.undo_turn()
        self.sim.undo_move(self.name_to_id["d"])
        self.sim.undo_move(self.name_to_id["c"])

        self.expect_board(
            """
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        )

        # Do something different
        self.sim.do_move(self.name_to_id["c"], models.LEFT)
        self.sim.do_move(self.name_to_id["d"], models.LEFT)
        self.sim.do_turn()
        self.expect_board(
            """
            .a...v.
            v^<.c<v
            >>^..d<
            .*.....
            .....*.
            ....>>b
            """,
            {
                "a": 50,
                "b": 99,
                "c": 1,
                "d": 41,
            },
        )

    def test_eat_food(self):
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.UP)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....B.
            ....>^.
            """,
            {
                "a": 50,
                "b": 100,
                "c": 1,
                "d": 41,
            },
        )
        self.sim.undo_turn()
        self.expect_board(
            """
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        )

    def test_starve(self):
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.UP)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....B.
            ....>^.
            """,
            {
                "a": 50,
                "b": 100,
                "c": 1,
                "d": 41,
            },
        )
        self.sim.do_move(self.name_to_id["a"], models.RIGHT)
        self.sim.do_move(self.name_to_id["b"], models.UP)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        # Snake c should starve on second turn
        self.expect_board(
            """
            .>a....
            .^<....
            >>^...v
            .*...bv
            .....^d
            ....>^.
            """,
            {
                "a": 49,
                "b": 99,
                "c": 0,
                "d": 40,
            },
        )

        # But c should come back after undo
        self.sim.undo_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....B.
            ....>^.
            """,
            {
                "a": 50,
                "b": 100,
                "c": 1,
                "d": 41,
            },
        )

    def test_move_out_of_bounds(self):
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.DOWN)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....*.
            .......
            """,
            {
                "a": 50,
                "b": 0,
                "c": 1,
                "d": 41,
            },
        )
        self.sim.undo_turn()
        self.expect_board(
            """
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        )

    def test_move_into_body(self):
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.RIGHT)
        self.sim.do_move(self.name_to_id["c"], models.RIGHT)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .a.....
            v^<...v
            >>^...v
            .*....d
            .....*.
            ....>>b
            """,
            {
                "a": 50,
                "b": 99,
                "c": 0,
                "d": 41,
            },
        )
        self.sim.undo_turn()
        self.expect_board(
            """
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        )

    def test_move_head_to_head(self):
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.UP)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....B.
            ....>^.
            """,
            {
                "a": 50,
                "b": 100,
                "c": 1,
                "d": 41,
            },
        )
        self.sim.do_move(self.name_to_id["a"], models.RIGHT)
        self.sim.do_move(self.name_to_id["b"], models.RIGHT)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.DOWN)
        self.sim.do_turn()
        self.expect_board(
            """
            .>a....
            .^<....
            >>^....
            .*.....
            .....>b
            ....>^.
            """,
            {
                "a": 49,
                "b": 99,
                "c": 0,
                "d": 0,
            },
        )
        self.sim.undo_turn()
        self.expect_board(
            """
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....B.
            ....>^.
            """,
            {
                "a": 50,
                "b": 100,
                "c": 1,
                "d": 41,
            },
        )

    def test_move_head_to_head_tie(self):
        self.sim.do_move(self.name_to_id["a"], models.UP)
        self.sim.do_move(self.name_to_id["b"], models.RIGHT)
        self.sim.do_move(self.name_to_id["c"], models.DOWN)
        self.sim.do_move(self.name_to_id["d"], models.LEFT)
        self.sim.do_turn()
        self.expect_board(
            """
            .a.....
            v^<....
            >>^....
            .*.....
            .....*.
            ....>>b
            """,
            {
                "a": 50,
                "b": 99,
                "c": 0,
                "d": 0,
            },
        )
        self.sim.undo_turn()
        self.expect_board(
            """
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        )

    def test_render(self):
        board_text = textwrap.dedent(
            """\
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            """
        )
        board = BoardBuilder(
            board_text,
            {
                "a": 51,
                "b": 100,
                "c": 2,
                "d": 42,
            },
        ).to_board()
        sim = Simulation(board)
        self.assertMultiLineEqual(
            sim.render(),
            board_text,
            "Render should return the same board that was built.",
        )
