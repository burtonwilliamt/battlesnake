from typing import Iterable, Mapping
import curses

import src.planning.multi_max as multi_max
import src.planning.simulation as simulation
import src.models as models
import tests.board_builder as board_builder

# snake_id, best_direction
'''
(Turn:3)(Snake:0)(Choice:left)
|Left   |Up     | R | D |
|v....vv|
|va<..Cv|
|>>^...d|
|....*..|
|.*.....|
|...>>b.|
VVVVVVVVV
Turn: 3  Snake: 1 Choice: up
| L |*R*| U | D |

'''


class DebugResult(multi_max.Result):

    def __init__(self, sim: simulation.Simulation):
        super().__init__(sim)
        self.debug_sim_render = sim.render()


class DebugLeafNode(multi_max.LeafNode):
    ResultType = DebugResult


class DebugSnakeDecision(multi_max.DecisionNode):
    LeafNodeType = DebugLeafNode

    def __init__(self, *, snk_id: int, moves: Mapping[models.Direction,
                                                      multi_max.DecisionNode]):
        super().__init__(snk_id=snk_id, moves=moves)
        self.debug_move_options = moves


class DecisionExplorer:
    DIRECTION_ORDER = (models.LEFT, models.UP, models.RIGHT, models.DOWN)

    def __init__(self, root: multi_max.DecisionNode, stdscr):
        self.stdscr = stdscr
        self.root = root
        top_result = root.get_result()
        if top_result.sim_render is None:
            raise AssertionError('Decision explorer only works in DEBUG.')

        board_rows = top_result.sim_render.splitlines()
        self.board_width = len(board_rows[0])
        self.board_height = len(board_rows)

        self.depth = self._max_depth(self.root)
        self.branch_choices = []

    def _max_depth(self, root: multi_max.DecisionNode) -> int:
        if isinstance(root, multi_max.LeafNode):
            return 1
        return max([self._max_depth(node) for node in root._moves.values()])

    def addstr_row(self, items: Iterable[str]):
        self.stdscr.addstr('|')
        for item in items:
            self.stdscr.addstr(f'{item:{self.board_width}}|')
        self.stdscr.addstr('\n')

    def display_snake_decision(self,
                               node: multi_max.SnakeDecision,
                               choice: models.Direction = None):
        # State label
        self.stdscr.addstr(
            f'(Turn:{node.turn})(Snake:{node.snk_id})(Choice:{node.best_direction.name})\n'
        )
        # Direction lables
        self.addstr_row([d.name.upper() for d in self.DIRECTION_ORDER])
        # Evaluate lables
        self.addstr_row([
            f'{hex(node.moves[d].node_evaluate(node.snk_id))[2:]:>{self.board_width}}'
            for d in self.DIRECTION_ORDER
        ])

        # The board
        boards_lines = []
        for d in self.DIRECTION_ORDER:
            child_result = node.moves[d].get_result()
            boards_lines.append(child_result.sim_render.splitlines())
        for i in range(self.board_height):
            self.addstr_row([board[i] for board in boards_lines])

        # Viewing selection indicator
        self.addstr_row([
            '*' * self.board_width if d == choice else ' ' * self.board_width
            for d in self.DIRECTION_ORDER
        ])

    def display_leaf_node(self, node: multi_max.LeafNode):
        self.stdscr.addstr(f'(Turn:{node.turn})(LEAF NODE)\n')
        self.stdscr.addstr(node.result.sim_render)

    def display_decision_node(self, node: multi_max.DecisionNode):
        if isinstance(node, multi_max.SnakeDecision):
            self.display_snake_decision(node, choice=None)
        elif isinstance(node, multi_max.LeafNode):
            self.display_leaf_node(node)
        else:
            raise AssertionError('Cannot draw unexpected node type')

    def display(self):
        win_y, win_x = self.stdscr.getmaxyx()
        max_nodes = int((win_y - 1) / (self.board_height + 4))
        nodes_to_skip = (len(self.branch_choices) + 1) - max_nodes
        node = self.root
        for choice in self.branch_choices:
            if not isinstance(node, multi_max.SnakeDecision):
                raise AssertionError('Cannot have branch choice for leaf node.')
            if nodes_to_skip > 0:
                nodes_to_skip -= 1
            else:
                self.display_snake_decision(node, choice=choice)
            node = node.moves[choice]
        self.display_decision_node(node)

        self.stdscr.addstr(win_y - 1, 0, 'WASD to select, Q to quit')

    def get_last_selected_node(self) -> multi_max.DecisionNode:
        node = self.root
        for choice in self.branch_choices:
            node = node.moves[choice]
        return node

    def run(self):
        while True:
            self.stdscr.erase()
            curses.curs_set(0)
            self.display()
            self.stdscr.refresh()
            selected_node = self.get_last_selected_node()

            c = self.stdscr.getkey()
            if c == 'q':
                break
            elif c == 'w':
                if len(self.branch_choices) == 0:
                    continue
                self.branch_choices.pop()
            elif c == 's':
                if isinstance(selected_node, multi_max.LeafNode):
                    continue
                self.branch_choices.append(self.DIRECTION_ORDER[0])
            elif c == 'd':
                if len(self.branch_choices) == 0:
                    continue
                i = self.DIRECTION_ORDER.index(self.branch_choices[-1])
                i = i + 1 % len(self.DIRECTION_ORDER)
                self.branch_choices[-1] = self.DIRECTION_ORDER[i]
            elif c == 'a':
                if len(self.branch_choices) == 0:
                    continue
                i = self.DIRECTION_ORDER.index(self.branch_choices[-1])
                i = i - 1
                self.branch_choices[-1] = self.DIRECTION_ORDER[i]


def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    return stdscr


if __name__ == '__main__':
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
    root = multi_max.SnakeDecision.make_tree(sim, depth=3)

    try:
        stdscr = init_curses()
        explr = DecisionExplorer(root, stdscr)
        explr.run()
    except KeyboardInterrupt:
        pass
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
