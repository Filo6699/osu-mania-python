import socket


class User:
    def __init__(self, conn: socket.socket) -> None:
        self.conn = conn
        self.id = -1
        self.auth_token = None
        self.username = None

    def send(self, pocket):
        pocket.send(self.conn)
