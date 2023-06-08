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
        print(data)
        connection.send(json.dumps(data).encode())

class LoginPocket(Pocket):
    def __init__(self, login, password) -> None:
        body = {
            "login": login,
            "password": password
        }
        super().__init__("auth", body)


POCKET_TYPES = {
    "auth": LoginPocket,
}

NO_TOKEN_POCKETS = [
    "auth"
]

# def get_pocket_type(data: dict):
#     try:
#         return POCKET_TYPES[data["type"]]
#     except:
#         return False

# def parse_pocket(data: bytes | str | dict) -> Pocket:
#     if isinstance(data, bytes):
#         try:
#             data = json.loads(data.decode())
#         except:
#             return None
#     if isinstance(data, str):
#         try:
#             data = json.loads(data)
#         except:
#             return None
#     if not isinstance(data, dict):
#         return None

#     ptype = get_pocket_type(data)
#     if ptype == LoginPocket:
#         return LoginPocket(data["login"], data["password"])
