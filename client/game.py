import pygame as pg
import threading
from client.scenes import Auth, SCENES
# from client.auth_old import AuthWindow
from client.network import Network
from client.player import Player


class Game:
    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen
        self.player = None
        self.players = []
        self.network = None
        self.authorized = False
    
    def main_loop(self):
        ...
        # font = pg.font.SysFont("Comic Sans", 36)
        # self.screen = pg.display.set_mode((700, 700))
        # clock = pg.time.Clock()
        # txt = font.render("Logged in as " + self.player.username, 1, (255, 255, 255))
        # self.screen.blit(txt, (5, 332))
        # while True:
        #     for e in pg.event.get():
        #         if e.type == pg.QUIT:
        #             pg.quit()
        #     pg.display.flip()

        #     clock.tick(5)
    
    def change_scene(self, scene: str, *args, **kwargs):
        self.scene = SCENES[scene](self.screen, self.network, self.change_scene, *args, **kwargs)

    def run(self, address):
        self.network = Network(address)
        pockets_thread = threading.Thread(target=self.network.supervise_loop, daemon=True)
        pockets_thread.start()
        self.network.add_listener(self.on_auth, 'auth')

        clock = pg.time.Clock()
        self.change_scene("auth")
        while True:
            ev = pg.event.get()
            for e in ev:
                if e.type == pg.QUIT:
                    pg.quit()
            self.scene.update(ev)

            self.scene.draw()
            pg.display.flip()
            clock.tick(60)
    
    def on_auth(self, pocket):
        if self.authorized:
            return
        if pocket['body']['correct'] == True:
            self.player = Player(uid=pocket['body']['id'], username=pocket['body']['username'])
            self.network.add_attributes({"auth": pocket['body']['token']})
            th = threading.Thread(target=self.main_loop)
            th.start()
            self.window.close()
            self.authorized = True
        else:
            self.scene.send_data({"correct": False})
