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

class GameScore(Pocket):
    def __init__(self, state) -> None:
        data = {
            "type": "game_state",
            "body": [
                {
                    "username": state["username"],
                    "score": state["score"],
                    "combo": state["combo"],
                }
            ]
        }
        super().__init__(data)

class GameScores(Pocket):
    def __init__(self, players) -> None:
        data = {
            "type": "game_state",
            "body": []
        }
        for u in players:
            udata = {
                "username": u['username'],
                "score": u['score'],
                "combo": u['combo'],
            }
            data['body'].append(udata)
        super().__init__(data)

class ChatMessage(Pocket):
    def __init__(self, message) -> None:
        data = {
            "type": "chat_message",
            "body": message
        }
        super().__init__(data)

class ChatMessages(Pocket):
    def __init__(self, msgs: list) -> None:
        data = {
            "type": "fetch_chat",
            "body": msgs
        }
        super().__init__(data)

class LobbyJoin(Pocket):
    def __init__(self, user: User) -> None:
        data = {
            "type": "lobby_player_join",
            "body": {
                "username": user.username,
                "play_count": user.play_count
            }
        }
        super().__init__(data)

class LobbyLeave(Pocket):
    def __init__(self, user: User) -> None:
        data = {
            "type": "lobby_player_leave",
            "body": {
                "username": user.username
            }
        }
        super().__init__(data)

class LobbyInfo(Pocket):
    def __init__(self, users: list) -> None:
        data = {
            "type": "lobby_fetch",
            "body": []
        }
        for u in users:
            data['body'].append({
                'username': u.username,
                'play_count': u.play_count
            })
        super().__init__(data)
