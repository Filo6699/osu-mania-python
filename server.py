import threading
import json
import socket


config = json.load(open('./config.json'))
host = config['host']
port = config['port']

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []

class User:
    def __init__(self, nickname, sock) -> None:
        self.nickname: str = nickname
        self.socket: socket.socket = sock

def broadcast(message: str):
    for client in clients:
        client.socket.send(message)

def handle(client: User):
    while True:
        try:
            message = client.socket.recv(1024)
            dec_message = message.decode('ascii')
            if dec_message == '/leave':
                clients.remove(client)
                broadcast(f'{client.nickname} left the chat'.encode('ascii'))
                client.socket.send('s/disconnect'.encode('ascii'))
                client.socket.close()
                break
            if dec_message == '/close_room':
                broadcast('[sys]: closing the room'.encode('ascii'))
                for c in clients:
                    c.socket.send('s/disconnect'.encode('ascii'))
                    c.socket.close()
                server.close()
                break
            broadcast(client.nickname.encode('ascii') + ': '.encode('ascii') + message)
        except:
            clients.remove(client)
            broadcast(f'{client.nickname} left the chat'.encode('ascii'))
            client.socket.close()
            break

def recieve():
    while True:
        client, addr = server.accept()
        print(f'{addr} has connected')
        client.send('Enter your nickname'.encode('ascii'))
        try:
            username = client.recv(256).decode('ascii')
        except Exception as err:
            client.send(f'An error has occured: {err}'.encode('ascii'))
            client.send('s/disconnect'.encode('ascii'))
            client.close()
            continue
        user = User(username, client)
        print(f'{addr} ({user.nickname}) has been added to the chat')
        broadcast(f'{user.nickname} joined the chat'.encode('ascii'))
        user.socket.send(f'Connected. Users: {", ".join([u.nickname for u in clients])}'.encode('ascii'))
        clients.append(user)

        thread = threading.Thread(target=handle, args=(user,))
        thread.start()

recieve()