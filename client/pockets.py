import socket
import json


class Pocket:
    def __init__(self, ptype: str, body: str | dict | list, attributes: dict={}) -> None:
        self.type = ptype
        self.body = body
        self.attributes = attributes
    
    def add_attributes(self, attributes: dict):
        self.attributes.update(attributes)

    def send(self, connection: socket.socket):
        data = {
            "type": self.type,
            "body": self.body
        }
        data.update(self.attributes)
        connection.send(json.dumps(data).encode())

class LoginPocket(Pocket):
    def __init__(self, login, password, attributes: dict = {}) -> None:
        body = {
            "login": login,
            "password": password
        }
        super().__init__("auth", body)

class RegisterPocket(Pocket):
    def __init__(self, login, username, password, attributes: dict = {}) -> None:
        body = {
            "login": login,
            "username": username,
            "password": password
        }
        super().__init__("register", body)

class GameStatePocket(Pocket):
    def __init__(self, game_state: dict, attributes: dict = {}) -> None:
        super().__init__("game_state", game_state, attributes)
