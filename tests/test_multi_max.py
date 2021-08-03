import unittest

import src.models as models
import src.planning.multi_max as multi_max
from src.planning.simulation import Simulation
from tests.board_builder import BoardBuilder


class TestMultiMax(unittest.TestCase):

    def test_pack_to_bits(self):
        self.assertEqual(bin(multi_max.pack_to_bits(255, 300, 69, 0)),
                         bin(0b11111111_11111111_01000101_00000000))

    def test_result_init(self):
        sim = Simulation(board=BoardBuilder(
            '''
            .v...
            .>b..
            ...av
            ...^<
            ''',
            {
                'a': 50,
                'b': 49,
            },
        ).to_board())
        res = multi_max.Result(sim)
        self.assertEqual(res.healths, [50, 49])
        self.assertEqual(res.num_dead, 0)
        self.assertEqual(res.lengths, [4, 3])

    def test_result_evaluate(self):
        sim = Simulation(board=BoardBuilder(
            '''
            .v...
            .>b..
            ...av
            ...^<
            ''',
            {
                'a': 50,
                'b': 49,
            },
        ).to_board())
        res1 = multi_max.Result(sim)
        self.assertEqual(bin(res1.evaluate(0)),
                         bin(multi_max.pack_to_bits(0, 0, 4, 50)))
        self.assertEqual(bin(res1.evaluate(1)),
                         bin(multi_max.pack_to_bits(0, 0, 3, 49)))

        sim.do_move(0, models.LEFT)
        sim.do_move(1, models.UP)
        sim.do_turn()
        res2 = multi_max.Result(sim)
        self.assertEqual(bin(res2.evaluate(0)),
                         bin(multi_max.pack_to_bits(1, 0, 4, 49)))
        self.assertEqual(bin(res2.evaluate(1)),
                         bin(multi_max.pack_to_bits(1, 0, 3, 48)))

        sim.do_move(0, models.LEFT)
        sim.do_move(1, models.RIGHT)
        sim.do_turn()
        res3 = multi_max.Result(sim)
        self.assertEqual(bin(res3.evaluate(0)),
                         bin(multi_max.pack_to_bits(2, 0, 4, 48)))
        self.assertEqual(bin(res3.evaluate(1)),
                         bin(multi_max.pack_to_bits(2, 0, 3, 47)))

    def test_result_reduce(self):
        sim = Simulation(board=BoardBuilder(
            '''
            .v...
            .>b..
            ...av
            ...^<
            ''',
            {
                'a': 50,
                'b': 49,
            },
        ).to_board())

        # Both snakes live
        sim.do_move(0, models.UP)
        sim.do_move(1, models.UP)
        sim.do_turn()
        res1 = multi_max.Result(sim)

        # B runs into snake a and dies
        sim.undo_turn()
        sim.undo_move(1)
        sim.do_move(1, models.RIGHT)
        sim.do_turn()
        res2 = multi_max.Result(sim)

        self.assertEqual(bin(res1.evaluate(0)),
                         bin(multi_max.pack_to_bits(1, 0, 4, 49)))
        self.assertEqual(bin(res1.evaluate(1)),
                         bin(multi_max.pack_to_bits(1, 0, 3, 48)))

        self.assertEqual(bin(res2.evaluate(0)),
                         bin(multi_max.pack_to_bits(1, 1, 4, 49)))
        self.assertEqual(bin(res2.evaluate(1)),
                         bin(multi_max.pack_to_bits(0, 1, 3, 0)))

        res_max_a = multi_max.Result.reduce([res1, res2], 0)
        res_max_b = multi_max.Result.reduce([res1, res2], 1)

        self.assertEqual(res_max_a, res2)
        self.assertEqual(res_max_b, res1)


class TestSituations(unittest.TestCase):
    def test_hallway(self):
        """Avoid the walls."""
        board = BoardBuilder('''
            >>>a....
            ''', {
            'a': 100,
        }).to_board()
        best_dir = multi_max.ideal_direction(board, depth=4)
        self.assertEqual(best_dir, models.RIGHT,
                         'Snake should go right in hallway.')

    def test_hail_mary(self):
        """Even when doomed the snake should try to stay alive."""
        board = BoardBuilder('''
            >>>a....
            ''', {
            'a': 100,
        }).to_board()
        best_dir = multi_max.ideal_direction(board, depth=8)
        self.assertEqual(
            best_dir, models.RIGHT,
            'Snake should go right in hallway even if it means eventual death.')

    def test_eat_to_live(self):
        """Don't starve."""
        board = BoardBuilder('''
            .....
            .>>a.
            ...*.
            ''', {
            'a': 1,
        }).to_board()
        best_dir = multi_max.ideal_direction(board, depth=3)
        self.assertEqual(
            best_dir, models.DOWN,
            'Snake should move down to eat.')
