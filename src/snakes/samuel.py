import src.models as models
from src.snakes.default import BattlesnakeServer
import src.planning.multi_max as multi_max


class Samuel(BattlesnakeServer):
    def handle_index(self):
        return models.BattlesnakeInfo(
            author='drzoid',
            color= '#039903',
            head= 'silly',
            tail= 'round-bum',
            version= '0.1.0',
        )

    def handle_move(self, data:models.Data) -> models.Direction:

        # Order snakes such that you are first
        data.board.snakes.sort(key=lambda snk: snk.id != data.you.id)
        best_direction = multi_max.ideal_direction(data.board, depth=2)
        print(f'Moving {best_direction}')
        return best_direction

