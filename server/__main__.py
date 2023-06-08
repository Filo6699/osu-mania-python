from server.network import Server
from server.db import users_db
from server.user import User
from server.pockets import WrongAuthDetails, UserInfo


def on_login(user: User, pocket: dict):
    # TODO: db.search(...)
    pocket = pocket['body']
    for id, data in users_db.items():
        if data["login"] == pocket["login"]:
            if data["password"] == pocket["password"]:
                user.auth_token = data["token"]
                user.id = id
                user.send(UserInfo(id, data))
                break
            else:
                user.send(WrongAuthDetails())
                break
    else:
        user.send(WrongAuthDetails())



if __name__ == "__main__":
    host = "localhost"
    port = 6699

    s = Server()
    s.start((host, port))
    s.add_listener(on_login, "auth")
