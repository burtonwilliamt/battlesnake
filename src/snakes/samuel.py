import random
from typing import List

import src.models as models
from src.snakes.default import BattlesnakeServer


def valid_directions(data:models.Data, snk:models.Battlesnake) -> List[models.Direction]:
    return [d for d in models.CARDINAL_FOUR if data.board.can_move(snk, d)]


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
        possible_directions = valid_directions(data, data.you)
        if len(possible_directions) == 0:
            possible_directions = models.CARDINAL_FOUR
        direction = random.choice(possible_directions)

        print(f'MOVE: {direction.name}')
        return direction

