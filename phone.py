import socket
import threading
import ctypes
from time import sleep


port = 6962
is_locked = False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host = socket.gethostbyname(host_name)
print(host)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

def handle(client: socket.socket):
    global is_locked
    while True:
        try:
            message = client.recv(256).decode()
            if not message:
                print('loss')
                is_locked = False
                return
            message = message[:-2]
            if message == 'f':
                ctypes.windll.user32.SwapMouseButton(True)
                continue
            if message == 'uf':
                ctypes.windll.user32.SwapMouseButton(False)
                continue
            if message == 't':
                ctypes.windll.user32.UnlockWorkStation()
                continue
            if message == 'l':
                ctypes.windll.user32.LockWorkStation()
                continue
            if message == 'ttl':
                is_locked = True
                continue
            if message == 'ul':
                is_locked = False
                continue
            print(message)
        except Exception as err:
            print(err)
            is_locked = False
            client.close()
            break

def recieve():
    while True:
        client, addr = server.accept()
        print(f'{addr} has connected')

        thread = threading.Thread(target=handle, args=(client, ), daemon=True)
        thread.start()
        
        while True:
            if is_locked:
                ctypes.windll.user32.LockWorkStation()
            sleep(3)

recieve()
