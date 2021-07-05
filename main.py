import os
import random
from typing import List
from enum import Enum
from dataclasses import dataclass

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""

class Coord:
  def __init__(self, data:dict):
    self.x = data['x']
    self.y = data['y']


class Tile(Enum):
  OUTSIDE = 0
  SNAKE = 1
  HAZARD = 2
  POTENTIAL_SNAKE = 3
  FOOD = 4
  EMPTY = 5


@dataclass
class Move:
  name: str
  rel_x: int
  rel_y: int


MOVES = [
  Move('up', 0, 1),
  Move('down', 0, -1),
  Move('left', -1, 0),
  Move('right', 1, 0),
]

class Battlesnake:
  def __init__(self, data:dict):
    self.id = data['id']
    self.name = data['name']
    self.health = data['health']
    self.body = [Coord(pt) for pt in data['body']]
    self.latency = data['latency']
    self.head = Coord(data['head'])
    self.length = data['length']
    self.shout = data['shout']
    self.squad = data['squad'] if 'squad' in data else None


class Board:
  def __init__(self, data:dict):
    # data fields
    self.height = data['height']
    self.width = data['width']
    self.food = [Coord(pt) for pt in data['food']]
    self.hazards = [Coord(pt) for pt in data['hazards']]
    self.snakes = [Battlesnake(snk) for snk in data['snakes']]

    # custom fields
    self.grid = [[Tile.EMPTY for _ in range(self.height)] for _ in range(self.width)]
    for fd in self.food:
      self.grid[fd.x][fd.y] = Tile.FOOD

    for hzd in self.hazards:
      self.grid[hzd.x][hzd.y] = Tile.HAZARD

    for snk in self.snakes:
      for segment in snk.body:
        self.grid[segment.x][segment.y] = Tile.SNAKE

  def get(self, x:int, y:int) -> Tile:
    if not (0 <= x < self.width and 0 <= y < self.height):
      return Tile.OUTSIDE
    else:
      return self.grid[x][y]

  def can_move(self, snk:Battlesnake, move:Move) -> bool:
    print(move)
    return self.get(snk.head.x+move.rel_x, snk.head.y+move.rel_y) in (Tile.EMPTY, Tile.FOOD)


class Data:
  def __init__(self, data:dict):
    self.game = None
    self.turn = data['turn']
    self.board = Board(data['board'])
    self.you = Battlesnake(data['you'])


def valid_moves(data:Data, snk:Battlesnake) -> List[Move]:
  return [mv for mv in MOVES if data.board.can_move(snk, mv)]


class BattlesnakeServer(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        # Go here for options: https://play.battlesnake.com/references/customizations/
        return {
            "apiversion": "1",
            "author": "drzoid",
            "color": "#039903",
            "head": "silly",
            "tail": "round-bum",
            "version": "0.1.0",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        print(f'Timout: {data["game"]["timeout"]}ms')
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = Data(cherrypy.request.json)

        # Choose a random direction to move in
        possible_moves = valid_moves(data, data.you)
        move = random.choice(possible_moves).name

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = BattlesnakeServer()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)

