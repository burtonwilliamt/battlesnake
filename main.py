import os
import sys
import getopt
from typing import Mapping

import cherrypy

from src.snakes.default import BattlesnakeServer
from src.snakes.igor import Igor
from src.snakes.samuel import Samuel


def snake_servers() -> Mapping[str, BattlesnakeServer]:
    """Return all the snake servers this webserver should host

    Returns:
        Mapping[str, BattlesnakeServer]: A mapping from the mount point to the
            server object that should be hosted there.
    """
    return {
        '/samuel': Samuel(),
        '/igor': Igor(),
    }


def config_cherrypy(port: int, auto_reload: bool):
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({
        'server.socket_port': int(os.environ.get('PORT', port)),
    })
    if not auto_reload:
        cherrypy.config.update({'global': {'engine.autoreload.on': False}})


def main(argv):
    auto_reload = False
    port = 80
    try:
        opts, args = getopt.getopt(argv, 'p:r', ['port=', 'auto_reload'])
    except getopt.GetoptError:
        print('main.py --port 8080 --auto_reload')

    print(opts)
    for opt, arg in opts:
        if opt in ('-p', '--port'):
            port = int(arg)
        elif opt in ('-r', '--auto_reload'):
            auto_reload = True
    config_cherrypy(port, auto_reload)

    for mnt, snk in snake_servers().items():
        cherrypy.tree.mount(snk, mnt)

    print('Starting Battlesnake Server...')
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main(sys.argv[1:])