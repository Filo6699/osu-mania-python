import socket
import json
import threading
from time import sleep
from random import random
from client.pockets import Pocket, FetchChat


class UnknownLoopBreak(Exception):
    """The pockets handle loop was stopped, but the connection still exists"""
    pass
class UnableToConnect(Exception):
    """Wasn't able to dfbs"""
    pass

class Network:
    """A socket with some extra features
    -------------
    name: str
        Username
    address: socket._Address
        Address. (e.g ('1.2.3.4', 6969))"""
    def __init__(self, address: tuple, attributes: dict={}):
        self.addr = address
        self.listeners = []
        self.disconnected = True
        self.failed_connections = 0
        self.attributes = attributes
        self.auth_data = None
        self.fetch_data = {}
    
    def add_listener(self, function, pocket_type: str | Pocket, use_count: int=-1, *args):
        if isinstance(pocket_type, Pocket):
            pocket_type = pocket_type.type
        self.listeners.append([function, pocket_type, use_count, *args])
    
    def add_attributes(self, attributes: dict):
        self.attributes.update(attributes)

    def connect(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.addr)
            self.disconnected = False
            self.failed_connections = 0
            print("[NETWORK] Connected.")
            return True
        except Exception as e:
            self.disconnect(e)
            return False

    def send(self, pocket: Pocket):
        if not self.disconnected:
            pocket.add_attributes(self.attributes)
            pocket.send(self.client)
            return True
        else:
            return False

    def handle_pockets_loop(self):
        while not self.disconnected:
            try:
                str_data = self.client.recv(1024).decode()
                data = json.loads(str_data)
            except Exception as err:
                t = type(err)
                if isinstance(err, ConnectionError):
                    self.disconnect(err)
                    break
                if t == json.JSONDecodeError:
                    continue
                raise err
            
            ptype = data['type']
            for l in self.listeners:
                if l[1] == ptype:
                    threading.Thread(target=l[0], args=[data, *l[3:]]).start()
                    l[2] -= 1
                    if l[2] == 0:
                        self.listeners.remove(l)
    
    def supervise_loop(self):
        while True:
            th = threading.Thread(target=self.handle_pockets_loop)
            th.start()
            th.join()
            if self.disconnected:
                while not self.connect():
                    self.failed_connections += 1
                    if self.failed_connections >= 5:
                        raise UnableToConnect
                    print(f"[NETWORK] Wasn't able to establish a connection #{self.failed_connections}. Retrying in 5 seconds...")
                    sleep(5)
                    continue
            else:
                raise UnknownLoopBreak
    
    def fetch_0(self, data, key):
        self.fetch_data[key] = data
    
    def fetch(self, pocket):
        self.send(pocket)
        key = random()
        while self.fetch_data.get(key):
            key = random()
        self.fetch_data[key] = {}
        self.add_listener(self.fetch_0, pocket.type, 1, key)
        i = 0
        while i < 10:
            if self.fetch_data[key]:
                data = self.fetch_data.pop(key)
                return data
            i += 1
            sleep(0.2)
        return None

    def sfetch_chat(self):
        poc = self.fetch(FetchChat())
        msgs = '\n'.join(poc['body']) + '\n'
        return msgs

    def disconnect(self, msg):
        if self.disconnected:
            return
        self.client.close()
        self.disconnected = True
        print("[NETWORK] Disconnected. Reason: ", msg)