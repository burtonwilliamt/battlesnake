import src.models as models
from src.snakes.default import BattlesnakeServer


class Igor(BattlesnakeServer):
    def handle_index(self):
        return models.BattlesnakeInfo(
            author='drzoid',
            color= '#23edce',
            head= 'silly',
            tail= 'round-bum',
            version= '0.1.0',
        )

    def handle_move(self, data:models.Data) -> models.Direction:
        return models.UP

