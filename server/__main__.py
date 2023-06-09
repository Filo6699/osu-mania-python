import json
from server.network import Server
from server.game import Game
from server.db import users_db
from server.user import User
from server.pockets import WrongAuthDetails, UserInfo, GameScore, GameScores


def on_login(user: User, pocket: dict):
    # TODO: db.search(...)
    pocket = pocket['body']
    for id, data in users_db.items():
        if data["login"] == pocket["login"]:
            if data["password"] == pocket["password"]:
                user.auth_token = data["token"]
                user.id = id
                user.username = data["username"]
                user.send(UserInfo(id, data))
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
        try:
            p['conn'].send(GameScore(u))
        except OSError:
            game.players.remove(p)


if __name__ == "__main__":
    config = json.load(open('./config.json'))
    host = config['host']
    port = config['port']

    server = Server()
    game = Game()
    server.start((host, port))
    server.add_listener(on_login, "auth")
    server.add_listener(on_game_state_update, "game_state")
