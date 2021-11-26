import src.models as models
from src.snakes.default import BattlesnakeServer
import src.planning.multi_max as multi_max
import config


class Samuel(BattlesnakeServer):

    def __init__(self):
        pass

    def handle_index(self):
        return models.BattlesnakeInfo(
            author='drzoid',
            color='#039903',
            head='silly',
            tail='round-bum',
            version='0.5.0',
        )

    def handle_move(self, data: models.Data) -> models.Direction:
        # TODO: Use a fringe calculation to optimally spend our time.
        pass
