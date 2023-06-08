import pygame as pg
import threading
from client.auth import AuthWindow
from client.network import Network
from client.player import Player
from PyQt6.QtWidgets import QApplication


host = "localhost"
port = 6699


class Game:
    def __init__(self) -> None:
        self.screen = None
        self.player = None
        self.players = []
        self.network = None
        self.authorized = False
    
    def main_loop(self):
        pg.init()
        font = pg.font.SysFont("Comic Sans", 36)
        self.screen = pg.display.set_mode((700, 700))
        clock = pg.time.Clock()
        txt = font.render("Logged in as " + self.player.username, 1, (255, 255, 255))
        self.screen.blit(txt, (5, 332))
        while True:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
            pg.display.flip()

            clock.tick(5)

    def run(self):
        self.network = Network((host, port))
        pockets_thread = threading.Thread(target=self.network.supervise_loop, daemon=True)
        pockets_thread.start()

        self.network.add_listener(self.on_auth, 'auth')

        self.app = QApplication([])
        self.window = AuthWindow(self.network)
        self.window.show()
        self.app.exec()
    
    def on_auth(self, pocket):
        if self.authorized:
            return
        if pocket['body']['correct'] == True:
            self.player = Player(uid=pocket['body']['id'], username=pocket['body']['username'])
            self.network.add_attributes({"auth": pocket['body']['token']})
            self.app.exit()
            th = threading.Thread(target=self.main_loop)
            th.start()
            self.authorized = True
        else:
            self.window.wrong_auth_details()
