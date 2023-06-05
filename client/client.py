import pygame as pg
import json
import threading
from datetime import datetime, timedelta
from network import Network


config = json.load(open('./config.json'))
host = config['host']
port = config['port']


pg.init()
clock = pg.time.Clock()
font = pg.font.SysFont('Comic Sans', 24)
msgs = []

class Message:
    def __init__(self, content) -> None:
        self.content = content
        self.created_at = datetime.now()
    
    def __str__(self) -> str:
        return self.content

class Chat:
    def __init__(self, send_function) -> None:
        self.is_toggled = False
        self.message = ""
        self.send_function = send_function
    
    def draw(self, screen: pg.Surface):
        if self.is_toggled:
            msg_pool = msgs

            pg.draw.rect(screen, (75, 75, 75), [3, screen.get_height() - 41, screen.get_width() - 4, 36])

            text_render = font.render(self.message, 1, (255, 255, 255))
            text_pos = [
                5,
                screen.get_height() - 5 - text_render.get_height()
            ]
            screen.blit(text_render, text_pos)
        else:
            msg_pool = [x for x in msgs if (datetime.now() - x.created_at).seconds <= 10]

        offset = 0
        for m in reversed(msg_pool):
            msg_render = font.render(m.content, 1, (200, 200, 200))
            msg_pos = [
                5,
                screen.get_height() - 5 - msg_render.get_height() * 2 - offset
            ]
            offset += msg_render.get_height()
            screen.blit(msg_render, msg_pos)
    
    def update(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if self.is_toggled:
                    if e.key == pg.K_RETURN:
                        length = len(self.message)
                        if length > 0 and length < 50:
                            pocket = {
                                "type": "chat_message",
                                "body": {
                                    "message": self.message
                                }
                            }
                            self.send_function(json.dumps(pocket).encode())
                            msgs.append(Message("You> " + self.message))
                        self.message = ""
                        self.is_toggled = False
                    else:
                        key = pg.key.name(e.key)
                        char = key.lower()
                        if char == 'backspace' and self.message:
                            self.message = self.message[:-1]
                        elif char == "space":
                            self.message += ' '
                        elif len(char) == 1 and len(username) < 50:
                            self.message += char
                else:
                    if e.key == pg.K_RETURN:
                        self.is_toggled = True
        

class Player:
    def __init__(self, p_id, name, pos=[200, 200]) -> None:
        self.id = p_id
        self.pos = pos
        self.name = name
        self.color = [255, 0, 0]
    
    def draw(self, surface: pg.Surface):
        pg.draw.rect(
            surface, self.color,
            [self.pos[0] - 25, self.pos[1] - 25, 
             50, 50]
        )
        text_render = font.render(self.name, 1, (255, 255, 255))
        text_pos = [
            self.pos[0] - text_render.get_width() / 2,
            self.pos[1] - 27 - text_render.get_height()
        ]
        surface.blit(text_render, text_pos)


class OwnPlayer(Player):
    def __init__(self, network: Network, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.network = network
        self.color = [0, 255, 0]
    
    def send_pos(self):
        data = {
            "type": "pos",
            "body": {
                "x": self.pos[0],
                "y": self.pos[1]
            }
        }
        self.network.client.send(json.dumps(data).encode())

    def move(self, addx=0, addy=0):
        self.pos[0] += addx
        self.pos[1] += addy
    
    def update(self, events):
        for e in events:
            if e.type == pg.QUIT:
                pg.quit()

            has_moved = False
            if e.type == pg.KEYDOWN:
                key = pg.key.name(e.key).lower()
                match key:
                    case 'a':
                        self.move(addx=-10)
                        has_moved = True
                    case 'd':
                        self.move(addx=10)
                        has_moved = True
                    case 'w':
                        self.move(addy=-10)
                        has_moved = True
                    case 's':
                        self.move(addy=10)
                        has_moved = True
            if has_moved:
                self.send_pos()


screen = pg.display.set_mode((700, 700))
players = []

def draw():
    screen.fill(0)
    for p in players:
        p.draw(screen)


def get_username_loop():
    username = ""
    do_update = True
    stage = 0
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()

            if e.type == pg.KEYDOWN:
                do_update = True
                if e.key == pg.K_RETURN and len(username) > 1:
                    stage = 1
                else:
                    key = pg.key.name(e.key)
                    char = key.lower()
                    if char == 'backspace' and username:
                        username = username[:-1]
                    elif char == "space":
                        username += ' '
                    elif len(char) == 1 and len(username) < 20:
                        username += char

        if do_update:
            screen.fill(0)
            if stage == 0:
                text = 'Enter your username: ' + username
            if stage == 1:
                text = 'Connecting...'
            text_render = font.render(text, 1, (255, 255, 255))
            screen.blit(text_render, [20, screen.get_height() / 2 - text_render.get_height() / 2])
            pg.display.flip()
            do_update = False

        if stage == 1:
            break
        clock.tick(60)
    return username


def handle_pockets(player: OwnPlayer):
    while True:
        data = player.network.client.recv(1024)
        if not data:
            print('debugfggdgdfg')
            player.network.client.close()
            break

        try:
            data = json.loads(data.decode())
        except json.JSONDecodeError:
            continue
        
        t = data['type']
        
        if t == 'player_id':
            player.id = data['body']['id']

        if t == 'pos':
            for p in data['body']:
                for sp in players:
                    if p['id'] != sp.id:
                        continue
                    sp.pos = [p['x'], p['y']]
        
        if t == 'add_players':
            for p in data['body']:
                players.append(Player(p['id'], p['username'], pos=p['pos']))
        
        if t == 'chat_message':
            msgs.append(Message(data['body']['message']))
            if len(msgs) > 10:
                msgs.pop(0)

        if t == 'remove_player':
            for p in players:
                if p.id == data['body']['id']:
                    players.remove(p)
                    break


def main_loop(player: OwnPlayer):
    chat = Chat(player.network.client.send)
    while True:
        events = pg.event.get()
        if not chat.is_toggled:
            player.update(events)
        chat.update(events)

        draw()
        chat.draw(screen)
        pg.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    username = get_username_loop()
    net = Network(username, (host, port))
    # try:
    pid = -1
    net.connect()
    player = OwnPlayer(net, pid, username)
    players.append(player)

    threading.Thread(target=handle_pockets, args=[player, ], daemon=True).start()

    print('switching to main loop')
    main_loop(player)
