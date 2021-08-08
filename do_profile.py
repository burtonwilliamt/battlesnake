import cProfile

import src.planning.multi_max as multi_max
import src.planning.simulation as simulation
import tests.board_builder as board_builder


def main():
    board = board_builder.BoardBuilder(
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
    sim = simulation.Simulation(board)
    root = multi_max.SnakeDecision.make_tree(sim, depth=4)

if __name__ == '__main__':
    cProfile.run('main()', 'output.prof')