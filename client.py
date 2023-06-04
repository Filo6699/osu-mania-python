import threading
import socket
import json
import os


config = json.load(open('./config.json'))
host = config['host']
port = config['port']

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

msgs = []

def recieve():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 's/disconnect':
                client.close()
                break
            msgs.append(message)
            print(message)
        except Exception as err:
            print(f'An error occured -> {err}')
            client.close()
            break

def write():
    while True:
        message = input('')
        if message == '/beu':
            os.system('cls')
            for m in msgs:
                print(m)
            continue
        try:
            client.send(message.encode('ascii'))
        except UnicodeEncodeError:
            print('ascii codec only')


recieve_thread = threading.Thread(target=recieve)
write_thread = threading.Thread(target=write)

recieve_thread.start()
write_thread.start()
