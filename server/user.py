import socket


class User:
    def __init__(self, conn: socket.socket) -> None:
        self.conn = conn
        self.id = -1
        self.auth_token = None
        self.username = None
        self.play_count = None

    def send(self, pocket):
        pocket.send(self.conn)
