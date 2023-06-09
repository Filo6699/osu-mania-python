import pygame as pg
import json
from client.game import Game
from client.scenes import load_fonts


def run():
    config = json.load(open('./config.json'))
    host = config['host']
    port = config['port']
    
    pg.init()
    load_fonts()
    
    screen = pg.display.set_mode((1200, 700))
    game = Game(screen)
    game.run((host, port))


if __name__ == "__main__":
    run()
