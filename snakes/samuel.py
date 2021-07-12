import random
from typing import List

import cherrypy

import models
from snakes.default import BattlesnakeServer


def valid_moves(data:models.Data, snk:models.Battlesnake) -> List[models.Move]:
    return [mv for mv in models.Move.CARDINAL_FOUR() if data.board.can_move(snk, mv)]


class Samuel(BattlesnakeServer):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # Go here for options: https://play.battlesnake.com/references/customizations/
        return {
            'apiversion': '1',
            'author': 'drzoid',
            'color': '#039903',
            'head': 'silly',
            'tail': 'round-bum',
            'version': '0.1.0',
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = models.Data(cherrypy.request.json)

        possible_moves = valid_moves(data, data.you)
        if len(possible_moves) == 0:
            possible_moves = models.Move.CARDINAL_FOUR()
        move = random.choice(possible_moves)

        print(f'MOVE: {move.name}')
        return move.json()

