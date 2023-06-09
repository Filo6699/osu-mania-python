from client.game import Game
import pygame as pg
from client.scenes import load_fonts


host = "localhost"
port = 6699


def run():
    pg.init()
    load_fonts()
    screen = pg.display.set_mode((1200, 700))
    game = Game(screen)
    game.run((host, port))


if __name__ == "__main__":
    run()
