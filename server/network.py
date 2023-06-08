import socket
import json
import threading
from pockets import NO_TOKEN_POCKETS
from server.pockets import Pocket
from server.user import User


class Server:
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = None
        self.listeners = []
        self.connections = []
        self.next_diid = 0
    
    def add_listener(self, function, pocket_type: str | Pocket, use_count: int=-1):
        if isinstance(pocket_type, Pocket):
            pocket_type = pocket_type.type
        self.listeners.append([function, pocket_type, use_count])
    
    def handle_new_connections(self):
        while True:
            conn, _ = self.server.accept()
            user = User(conn)
            self.connections.append(user)
            th = threading.Thread(target=self.handle_pockets_loop, args=[user, ])
            th.start()
            self.next_diid += 1
    
    def start(self, address):
        self.address = address
        self.server.bind(address)
        self.server.listen(1)
        th = threading.Thread(target=self.handle_new_connections)
        th.start()
    
    def handle_pockets_loop(self, user: User):
        while True:
            try:
                str_data = user.conn.recv(1024).decode()
                data = json.loads(str_data)
            except Exception as err:
                t = type(err)
                if isinstance(err, ConnectionError):
                    self.disconnect(user)
                    break
                if t == json.JSONDecodeError:
                    print('js')
                    continue
                raise err
            
            ptype = data['type']

            try:
                if data["auth"] != user.auth_token:
                    continue
            except:
                if ptype not in NO_TOKEN_POCKETS:
                    continue
                pass

            for l in self.listeners:
                if l[1] == ptype:
                    threading.Thread(target=l[0], args=[user, data, ]).start()
                    l[2] -= 1
                    if l[2] == 0:
                        self.listeners.remove(l)
    
    def disconnect(self, user: User):
        user.conn.close()
