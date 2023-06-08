import socket
import json
from server.user import User


class Pocket:
    def __init__(self, data: dict) -> None:
        self.data = data
    
    def send(self, conn: socket.socket):
        conn.send(json.dumps(self.data).encode())


class GameStatePocket(Pocket):
    def __init__(self, game_state: dict) -> None:
        data = {
            "type": "game_state",
            "body": game_state
        }
        super().__init__(data)

class UserInfo(Pocket):
    def __init__(self, uid, data: dict) -> None:
        data = {
            "type": "auth",
            "body": {
                "correct": True,
                "id": uid,
                "username": data["username"],
                "token": data["token"]
            }
        }
        super().__init__(data)

class WrongAuthDetails(Pocket):
    def __init__(self) -> None:
        data = {
            "type": "auth",
            "body": {
                "correct": False
            }
        }
        super().__init__(data)
