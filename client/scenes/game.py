from pygame import Surface, KEYDOWN, draw
from pygame.font import Font
from client.scenes.scene_components import Scene
from client.network import Network
from client.pockets import GameStatePocket


def load_fonts():
    GameScene.leaderboard_font = Font(None, 34)


class Player:
    def __init__(self, username) -> None:
        self.username = username
        self.game_state = {
            "username": username,
            "score": 0,
            "combo": 0,
            "scores": {
                "300": 0,
                "100": 0,
                "50": 0,
                "0": 0
            }
        }


class GameScene(Scene):
    leaderboard_font: Font = None

    def __init__(self, screen: Surface, net: Network, change_scene) -> None:
        super().__init__(screen, change_scene)
        self.network = net
        self.network.add_listener(self.send_data, "game_state")
        self.self_state = Player(self.network.auth_data['username'])
        self.players = []
        self.players.append(self.self_state)
    
    def send_data(self, data: dict):
        for p in data['body']:
            try:
                for su in self.players:
                    if su.username == p['username']:
                        u = su.game_state
                        break
                else:
                    1/0
            except ZeroDivisionError:
                u = Player(p['username'])
                self.players.append(u)
                u = u.game_state
            if u['username'] == self.self_state.username:
                continue
            u['score'] = p['score']
            u['combo'] = p['combo']

    def send_game_state(self):
        self.network.send(GameStatePocket(self.self_state.game_state))
    
    def draw_leaderboard(self):
        src = self.screen

        lb = sorted([p.game_state for p in self.players], key=lambda x:x['score'], reverse=True)
        place = 1
        for u in lb:
            yoffset = (place - 1) * 80 + self.screen.get_height() / 2 - 120
            username = self.leaderboard_font.render(u['username'], 1, (255, 255, 255))
            u_pos = [
                5,
                yoffset + 8
            ]
            score = self.leaderboard_font.render(str(u['score']), 1, (255, 255, 255))
            s_pos = [
                5,
                yoffset + 34
            ]
            combo = self.leaderboard_font.render("x" + str(u['combo']), 1, (255, 255, 255))
            c_pos = [
                170 - combo.get_width(),
                yoffset + 34
            ]

            draw.rect(src, (10, 10, 60), [
                1, yoffset, 180, 70
            ])
            src.blit(username, u_pos)
            src.blit(score, s_pos)
            src.blit(combo, c_pos)
            place += 1
    
    def note_hit(self, score):
        self.self_state.game_state['score'] += score
        self.self_state.game_state['combo'] += 1
        self.send_game_state()
    
    def draw(self):
        scr = self.screen
        scr.fill(0)
        self.draw_leaderboard()
    
    def update(self, events):
        for e in events:
            if e.type == KEYDOWN:
                self.note_hit(300)
