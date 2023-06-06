import socket
import json


class Network:
    """A socket with some extra features
    -------------
    name: str
        Username
    address: socket._Address
        Address. (e.g ('1.2.3.4', 6969))"""
    def __init__(self, name: str, address: tuple):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = address
        self.name = name

    def connect(self):
        try:
            self.client.connect(self.addr)
        except Exception as e:
            self.disconnect(e)

    def send(self, data):
        try:
            self.client.send(json.dumps(data).encode())
            
            d = self.client.recv(1024).decode()

            keys = [key for key in data.keys()]
            return json.loads(d)[str(keys[0])]
        except socket.error as e:
            self.disconnect(e)

    def disconnect(self, msg):
        self.client.close()
        raise msg