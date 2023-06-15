import json
from server.network import Server
from server.game import Game
from server.db import users_db
from server.user import User
from server.pockets import (
    WrongAuthDetails, 
    UserInfo, 
    GameScore, 
    ChatMessage, 
    ChatMessages, 
    LobbyJoin, 
    LobbyLeave,
    LobbyInfo,
)
from datetime import datetime


def on_login(user: User, pocket: dict):
    # TODO: db.search(...)
    pocket = pocket['body']
    for id, data in users_db.items():
        if data["login"] == pocket["login"]:
            if data["password"] == pocket["password"]:
                user.auth_token = data["token"]
                user.id = id
                user.username = data["username"]
                user.play_count = data['play_count']
                user.send(UserInfo(id, data))
                u = {
                    "username": user.username,
                    "play_count": user.play_count,
                    "score": 0,
                    "combo": 0,
                    "conn": user
                }
                for us in game.players:
                    us['conn'].send(LobbyJoin(user))
                game.players.append(u)
                game.add_player(user)
                break
            else:
                user.send(WrongAuthDetails())
                break
    else:
        user.send(WrongAuthDetails())

def on_game_state_update(user: User, pocket: dict):
    try:
        for su in game.players:
            if su['username'] == user.username:
                u = su
                break
        else:
            1/0
    except ZeroDivisionError:
        u = {
            "username": user.username,
            "play_count": user.play_count,
            "score": pocket['body']['score'],
            "combo": pocket['body']['combo'],
            "conn": user
        }
        game.players.append(u)
    u['score'] = pocket['body']['score']
    u['combo'] = pocket['body']['combo']
    for p in game.players:
        if p['username'] == user.username:
            continue
        p['conn'].send(GameScore(u))

def on_msg(user: User, pocket: dict):
    n = datetime.now()
    hh = n.hour
    mm = n.minute
    ss = n.second
    msg = f"[{hh:2}:{mm:2}:{ss:2}] {user.username}> {pocket['body']}"
    poc = ChatMessage(msg)
    game.chat_msgs.append(msg)
    for p in game.players:
        p['conn'].send(poc)

def udisc(user):
    try:
        for u in game.players:
            if u["username"] == user.username:
                game.players.remove(u)
                game.remove_player(user)
                for us in game.players:
                    us['conn'].send(LobbyLeave(user))
    except ValueError:
        pass

def fetch_chat_req(user: User, _):
    user.send(ChatMessages(game.chat_msgs[-7:]))

def fetch_lobby(user: User, _):
    user.send(LobbyInfo(game.slots))


if __name__ == "__main__":
    config = json.load(open('./config.json'))
    host = config['host']
    port = config['port']

    server = Server(udisc)
    game = Game()
    server.start((host, port))
    server.add_listener(on_login, "auth")
    server.add_listener(on_game_state_update, "game_state")
    server.add_listener(on_msg, "chat_message")
    server.add_listener(fetch_chat_req, "fetch_chat")
    server.add_listener(fetch_lobby, "lobby_fetch")
