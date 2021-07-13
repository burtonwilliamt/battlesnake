import random

import cherrypy

import src.models as models


class BattlesnakeServer:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.handle_index().json()

    def handle_index(self) -> models.BattlesnakeInfo:
        return models.BattlesnakeInfo()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        self.handle_start(models.Data(cherrypy.request.json))
        return 'ok'

    def handle_start(self, data: models.Data):
        print('START')
        print(f'Timeout: {data.game.timeout}ms')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        direction = self.handle_move(models.Data(cherrypy.request.json))
        return models.Move(direction).json()

    def handle_move(self, data:models.Data) -> models.Direction:
        possible_directions = models.CARDINAL_FOUR
        direction = random.choice(possible_directions)
        move = models.Move(direction)

        print(f'MOVE: {move}')

        return move.json()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        self.handle_end(models.Data(cherrypy.request.json))
        return 'ok'

    def handle_end(self, data:models.Data):
        print('END')
