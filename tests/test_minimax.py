import unittest

from absl.testing import parameterized

import src.models as models
from src.planning import minimax
from src.planning.simulation import Simulation
from tests.board_builder import BoardBuilder


class TestMinimax(parameterized.TestCase):
    @parameterized.named_parameters(
        dict(
            testcase_name="both_alive",
            board_str="""
                .>a.
                .>b.
            """,
            healths={"a": 100, "b": 100},
            expected_value=0b10,
        ),
        dict(
            testcase_name="youre_dead",
            board_str="""
                .>a.
                .>b.
            """,
            healths={"a": 100, "b": 0},
            expected_value=0b11,
        ),
        dict(
            testcase_name="im_dead",
            board_str="""
                .>a.
                .>b.
            """,
            healths={"a": 0, "b": 100},
            expected_value=0b00,
        ),
        dict(
            testcase_name="both_dead",
            board_str="""
                .>a.
                .>b.
            """,
            healths={"a": 0, "b": 0},
            expected_value=0b01,
        ),
    )
    def test_evaluate(
        self, board_str: str, healths: dict[str, int], expected_value: int
    ):
        sim = Simulation(board=BoardBuilder(board_str, healths).to_board())
        self.assertEqual(minimax.evaluate(sim), expected_value)