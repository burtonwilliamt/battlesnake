import src.models as models
from src.snakes.default import BattlesnakeServer
import src.planning.multi_max as multi_max
import config


class Samuel(BattlesnakeServer):

    def __init__(self):
        self.calculation_depth = 3

    def handle_index(self):
        return models.BattlesnakeInfo(
            author='drzoid',
            color='#039903',
            head='silly',
            tail='round-bum',
            version='0.5.0',
        )

    def update_calculation_depth(self, data: models.Data):
        print(f'Latency is "{data.you.latency}"')
        # First call, no latency
        if data.you.latency is None:
            pass
        # If we are getting dangerously close to the limit, decrease depth.
        elif data.you.latency == 0.0 or data.you.latency > data.game.timeout * 0.5:
            self.calculation_depth -= 1
        # If we have plenty of extra time, look further.
        elif data.you.latency < data.game.timeout * 0.1:
            self.calculation_depth += 1

        self.calculation_depth = min(max(self.calculation_depth, 1), 4)

    def handle_move(self, data: models.Data) -> models.Direction:
        self.update_calculation_depth(data)

        # Order snakes such that you are first
        data.board.snakes.sort(key=lambda snk: snk.id != data.you.id)
        best_direction = multi_max.ideal_direction(data.board,
                                                   depth=self.calculation_depth)
        print(f'Looking {self.calculation_depth} steps into future.')
        return best_direction
