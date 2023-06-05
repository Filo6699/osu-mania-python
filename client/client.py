import pygame as pg
import json
import threading
from network import Network


config = json.load(open('./config.json'))
host = config['host']
port = config['port']


pg.init()
clock = pg.time.Clock()
font = pg.font.SysFont('Comic Sans', 24)

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
    
    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
            if e.type == pg.KEYDOWN:
                key = pg.key.name(e.key).lower()
                has_moved = False
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
    pg.display.flip()

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


def handle_pockets(net: Network):
    while True:
        data = net.client.recv(1024)
        if not data:
            print('debugfggdgdfg')
            net.client.close()
            break

        try:
            data = json.loads(data.decode())
        except json.JSONDecodeError:
            continue
        
        t = data['type']
        
        if t == 'pos':
            for p in data['body']:
                for sp in players:
                    if p['id'] != sp.id:
                        continue
                    sp.pos = [p['x'], p['y']]
        
        if t == 'add_players':
            print('add players')
            for p in data['body']:
                players.append(Player(p['id'], p['username'], pos=p['pos']))


# def send_pockets(player: OwnPlayer):
#     player.send_pos()


def main_loop(player: OwnPlayer):
    while True:
        player.update()
        draw()

        clock.tick(60)

if __name__ == "__main__":
    username = get_username_loop()
    net = Network(username, (host, port))
    try:
        pid = net.connect()
        player = OwnPlayer(net, pid, username)
        players.append(player)

        threading.Thread(target=handle_pockets, args=[net, ], daemon=True).start()
        # threading.Thread(target=send_pockets, args=[player, ], daemon=True).start()

        print('switching to main loop')
        main_loop(player)
    except Exception as e:
        print(e, " Wasn't able to connect to the server, exiting...")
