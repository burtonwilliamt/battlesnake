import unittest

from src.models import Board, UP, DOWN, LEFT, RIGHT
from src.planning.simulation import BoardState, TurnBuilder

from tests.board_builder import BoardBuilder


class TestSimulation(unittest.TestCase):

    def assert_board_state_equals_board(self, board_state:BoardState, board:Board):
        self.assertEqual(board_state.height, board.height)
        self.assertEqual(board_state.width, board.width)

        self.assertCountEqual(board_state.food, [(food.x, food.y) for food in board.food])

        self.assertEqual(len(board_state.snakes), len(board.snakes))
        for i, bs_snake in enumerate(board_state.snakes):
            b_snake = board.snakes[i]
            self.assertEqual(bs_snake.health, b_snake.health)
            self.assertEqual(len(bs_snake.body), len(b_snake.body))
            for j, bs_segment in enumerate(bs_snake.body):
                self.assertEqual(bs_segment[0], b_snake.body[j].x)
                self.assertEqual(bs_segment[1], b_snake.body[j].y)


    def test_board_state_from_board(self):
        board = BoardBuilder(
            '''
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            ''', {
                'a': 51,
                'b': 100,
                'c': 2,
                'd': 42,
            }).to_board()
        board_state = BoardState.from_board(board)

        self.assert_board_state_equals_board(board_state, board)
        self.assertEqual(board_state.turn, 0)

    def test_all_snakes_move(self):
        board = BoardBuilder(
            '''
            v....vv
            va<..Cv
            >>^...d
            .*.....
            .....*.
            ...>>b.
            ''', {
                'a': 51,
                'b': 100,
                'c': 2,
                'd': 42,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((UP, RIGHT, DOWN, DOWN))

        new_board = BoardBuilder(
            '''
            .a...v.
            v^<..vv
            >>^..cv
            .*....d
            .....*.
            ....>>b
            ''', {
                'a': 50,
                'b': 99,
                'c': 1,
                'd': 41,
            }).to_board()
        self.assert_board_state_equals_board(new_state, new_board)
        self.assertEqual(new_state.turn, 1)


    def test_snake_starves(self):
        board = BoardBuilder(
            '''
            .......
            .>>>a..
            .......
            ''', {
                'a': 1,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((RIGHT,))

        self.assertEqual(new_state.snakes[0].health, 0)

    def test_snake_out_of_bounds(self):
        board = BoardBuilder(
            '''
            .....
            .>>>a
            .....
            ''', {
                'a': 5,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((RIGHT,))

        self.assertEqual(new_state.snakes[0].health, 0)

    def test_follow_tail(self):
        board = BoardBuilder(
            '''
            .....
            .va..
            .>^..
            ''', {
                'a': 5,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((LEFT,))

        new_board = BoardBuilder(
            '''
            .....
            .a<..
            .>^..
            ''', {
                'a': 4,
            }).to_board()
        self.assert_board_state_equals_board(new_state, new_board)


    def test_eat_self(self):
        board = BoardBuilder(
            '''
            .v...
            .va..
            .>^..
            ''', {
                'a': 5,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((LEFT,))

        self.assertEqual(new_state.snakes[0].health, 0)

    def test_eat_neck(self):
        board = BoardBuilder(
            '''
            .....
            >>>a.
            .....
            ''', {
                'a': 5,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((LEFT,))

        self.assertEqual(new_state.snakes[0].health, 0)

    def test_collide_with_other_snake(self):
        board = BoardBuilder(
            '''
            .b<<.
            ..a..
            ..^..
            ''', {
                'a': 5,
                'b': 15,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((UP, LEFT))

        self.assertEqual(new_state.snakes[0].health, 0)
        self.assertEqual(new_state.snakes[1].health, 14)

    def test_head_to_head(self):
        board = BoardBuilder(
            '''
            .....
            >b.a<
            ...>^
            ''', {
                'a': 5,
                'b': 15,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((LEFT, RIGHT))

        self.assertEqual(new_state.snakes[0].health, 4)
        self.assertEqual(new_state.snakes[1].health, 0)

    def test_food_persists(self):
        board = BoardBuilder(
            '''
            .....
            .>>a.
            ..*..
            ''', {
                'a': 5,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((RIGHT,))

        new_board = BoardBuilder(
            '''
            .....
            ..>>a
            ..*..
            ''', {
                'a': 4,
            }).to_board()
        self.assert_board_state_equals_board(new_state, new_board)

    def test_food_gets_eaten(self):
        board = BoardBuilder(
            '''
            .....
            .>>a*
            .....
            ''', {
                'a': 5,
            }).to_board()
        board_state = BoardState.from_board(board)

        new_state = board_state.do_turn((RIGHT,))

        new_board = BoardBuilder(
            '''
            .....
            ..>>A
            .....
            ''', {
                'a': 100,
            }).to_board()
        self.assert_board_state_equals_board(new_state, new_board)