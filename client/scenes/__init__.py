from client.scenes.auth import Auth
from client.scenes.register import Register
from client.scenes.game import GameScene
from client.scenes.lobby import Lobby

from client.scenes.scene_components import load_fonts as l1
from client.scenes.game import load_fonts as l2


SCENES = {
    "auth": Auth,
    "register": Register,
    "game": GameScene,
    "lobby": Lobby
}


def load_fonts():
    l1()
    l2()
