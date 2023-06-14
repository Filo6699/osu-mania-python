import pygame as pg
from pygame import SRCALPHA
import threading
from client.scenes import SCENES
from client.network import Network


class Game:
    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen
        self.auth_data = None
        self.network = None
        self.authorized = False
        self.fade_in = 0
    
    def change_scene(self, scene: str, *args, **kwargs):
        k = 10
        while k <= 120:
            sc = pg.Surface(self.screen.get_size(), flags=SRCALPHA)
            sc.fill((0, 0, 0, k))
            self.screen.blit(sc, (0, 0))
            k += 8
            pg.display.flip()
            self.clock.tick(60)
        self.fade_in = 255
        self.scene = SCENES[scene](self.screen, self.network, self.change_scene, *args, **kwargs)

    def run(self, address):
        self.network = Network(address)
        pockets_thread = threading.Thread(target=self.network.supervise_loop, daemon=True)
        pockets_thread.start()
        self.network.add_listener(self.on_auth, 'auth', 1)

        self.clock = pg.time.Clock()
        # self.change_scene("lobby")
        self.change_scene("auth")
        while True:
            ev = pg.event.get()
            for e in ev:
                if e.type == pg.QUIT:
                    pg.quit()
            self.scene.update(ev)

            self.scene.draw()
            if self.fade_in > 0:
                sc = pg.Surface(self.screen.get_size(), flags=SRCALPHA)
                sc.fill((0, 0, 0, self.fade_in))
                self.screen.blit(sc, (0, 0))
                self.fade_in -= 24
            pg.display.flip()
            self.clock.tick(60)
    
    def on_auth(self, pocket):
        if self.authorized:
            return
        if pocket['body']['correct'] == True:
            self.network.auth_data = {
                "uid": pocket['body']['id'],
                "username": pocket['body']['username']
            }
            self.network.add_attributes({"auth": pocket['body']['token']})
            self.authorized = True
            self.change_scene("lobby")
        else:
            self.scene.send_data({"correct": False})
            self.network.add_listener(self.on_auth, 'auth', 1)
