import os
import random
from typing import List
from enum import Enum
from dataclasses import dataclass

import cherrypy

import models
from snakes.samuel import Samuel
from snakes.medusa import Medusa

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update(
        {'server.socket_port': int(os.environ.get('PORT', '8080')),}
    )
    print('Starting Battlesnake Server...')
    cherrypy.tree.mount(Samuel(), '/samuel')
    cherrypy.tree.mount(Medusa(), '/medusa')

    cherrypy.engine.start()
    cherrypy.engine.block()
