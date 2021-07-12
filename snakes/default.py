import random

import cherrypy

import models


class BattlesnakeServer:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # Go here for options: https://play.battlesnake.com/references/customizations/
        return {
            "apiversion": "1",
            "author": "unowned",
            "color": "#606060",
            "head": "default",
            "tail": "default",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        data = models.Data(cherrypy.request.json)

        print("START")
        print(f'Timeout: {data.game.timeout}ms')
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = models.Data(cherrypy.request.json)

        possible_moves = models.MOVES
        move = random.choice(possible_moves).name

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        data = models.Data(cherrypy.request.json)

        print("END")
        return "ok"
