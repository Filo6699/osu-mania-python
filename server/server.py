import socket
import json
import threading
from time import sleep

config = json.load(open('./config.json'))
host = config['host']
port = config['port']

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

player_id = 0
players = []

class Player:
    def __init__(self, p_id, username, conn: socket.socket, pos) -> None:
        self.id = p_id
        self.username = username
        self.socket = conn
        self.pos = pos

def handle_pockets(player: Player):
    while True:
        try:
            data = player.socket.recv(1024)
        except ConnectionResetError:
            data = None
        if not data:
            players.remove(player)
            for p in players:
                pocket = {
                    "type": "remove_player",
                    "body": {
                        "id": player.id
                    }
                }
                p.socket.send(json.dumps(pocket).encode())

                pocket = {
                    "type": "chat_message",
                    "body": {
                        "message": player.username + " has left the game"
                    }
                }
                p.socket.send(json.dumps(pocket).encode())
            player.socket.close()
            break
        try:
            data = json.loads(data.decode())
        except json.JSONDecodeError:
            continue
        
        t = data['type']

        if t == 'pos':
            player.pos = [
                data['body']['x'],
                data['body']['y'],
            ]
        
        if t == 'chat_message':
            for p in players:
                if p != player:
                    data['body']['message'] = player.username + "> " + data['body']['message']
                    p.socket.send(json.dumps(data).encode())

def new_player(player: Player):
    pocket = {"type": "add_players", "body": []}
    pocket['body'].append({"id": player.id, "username": player.username, "pos": player.pos})
    bts = json.dumps(pocket).encode()

    chat_pocket = {
        "type": "chat_message",
        "body": {
            "message": player.username + " has joined the game"
        }
    }
    bts2 = json.dumps(chat_pocket).encode()
    for p in players:
        p.socket.send(bts)
        p.socket.send(bts2)


def handle_connection():
    global player_id
    while True:
        conn, addr = server.accept()
        try:
            username = conn.recv(1024).decode()
            conn.send(json.dumps({"type": "player_id", "body": {"id": player_id}}).encode())
        except:
            continue

        if len(players) > 0:
            pocket = {"type": "add_players", "body": []}
            for p in players:
                pocket['body'].append({"id": p.id, "username": p.username, "pos": p.pos})
            print(pocket)
            conn.send(json.dumps(pocket).encode())
        
        player = Player(player_id, username, conn, [200, 200])
        new_player(player)
        players.append(player)
        player_id += 1
        print(addr, ' has connected')
        th = threading.Thread(target=handle_pockets, args=[player, ], daemon=True)
        th.start()

th = threading.Thread(target=handle_connection)
th.start()

tps = 20
while True:
    if len(players) > 1:
        for p in players:
            data = {
                "type": "pos",
                "body": []
            }
            for sub_p in players:
                if p == sub_p:
                    continue
                data['body'].append({
                    "id": sub_p.id,
                    "x": sub_p.pos[0],
                    "y": sub_p.pos[1]
                })
            try:
                p.socket.send(json.dumps(data).encode())
            except ConnectionError:
                pass
            
    sleep(1 / tps)
