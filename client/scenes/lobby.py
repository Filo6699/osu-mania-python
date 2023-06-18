import threading
from time import sleep
from pygame import Surface, KEYDOWN, draw
from pygame.font import Font
from client.scenes.scene_components import Scene, Form, Map, Button, Label, TextEdit, Slot
from client.network import Network
from client.pockets import ChatMessage, FetchLobby


class Lobby(Scene):
    def __init__(self, screen: Surface, net: Network, change_scene) -> None:
        super().__init__(screen, change_scene)
        self.net = net
        self.form = Form(screen.get_size())
        self.form.border_radius = 0
        self.form.border_color = (0, 0, 0, 0)
        margin = screen.get_width() / 70
        for i in range(5):
            self.form.add_component(Slot(
                "", -1,
                (screen.get_width() / 2 - margin * 2, (screen.get_height() * 0.6 - margin * 2) / 5),
                "us" + str(i + 1),
                position=[margin, margin + ((screen.get_height() * 0.65 - margin * 2) / 5) * i]))
        self.players = 0
        
        self.net.add_listener(self.new_player, "lobby_join")
        self.net.add_listener(self.player_left, "lobby_leave")

        self.chat_edit = TextEdit((screen.get_width(), 0), "chat_edit", [0, 0], "Enter a message...")
        self.chat_edit.pos = [
            0, screen.get_height() - self.chat_edit.sizes[1]
        ]
        self.chat_edit.color = (100, 100, 100)
        self.chat_edit.enter_pressed = self.send_message
        self.chat_edit.symbol_limit = 83
        self.form.add_component(self.chat_edit)

        self.chat = Label("", (screen.get_width(), screen.get_height() * 0.35 - self.chat_edit.sizes[1]), "chat", [5, screen.get_height() * 0.65 + 10])
        self.chat.is_centered = False
        self.form.add_component(self.chat)

        self.map = Map((screen.get_width() / 2 - margin * 2, screen.get_height() / 6), "map_card", [screen.get_width() / 2 + margin, margin])
        self.form.add_component(self.map)

        self.skip_button = Button(
            "Skip the map\n0/3",
            (screen.get_width() / 6, screen.get_height() / 6),
            "skip",
            [screen.get_width() * 5 / 6 - margin, screen.get_height() / 2 - margin * 2]
        )
        self.skip_button.border_radius = 0
        self.skip_button.outline_color = (120, 120, 120)
        self.skip_button.color = (120, 120, 120)
        self.skip_button.font_color = (255, 255, 255)
        self.skip_button.pressed_color = (150, 150, 150)
        self.form.add_component(self.skip_button)

        self.play_button = Button(
            "Play the map\n0/3",
            (screen.get_width() / 6, screen.get_height() / 6),
            "skip",
            [screen.get_width() / 2 + margin, screen.get_height() / 2 - margin * 2]
        )
        self.play_button.border_radius = 0
        self.play_button.outline_color = (120, 120, 120)
        self.play_button.color = (120, 120, 120)
        self.play_button.font_color = (255, 255, 255)
        self.play_button.pressed_color = (150, 150, 150)
        self.form.add_component(self.play_button)

        self.net.add_listener(self.send_data, "chat_message")
        self.net.add_listener(self.send_data, "lobby_player_join")
        self.net.add_listener(self.send_data, "lobby_player_leave")

        th = threading.Thread(target=self.fetch_loop)
        th.start()
    
    def fetch_loop(self):
        while True:
            pocket = self.net.sfetch_chat()
            if pocket:
                self.chat.text = pocket
            
            pocket = self.net.fetch(FetchLobby())
            if pocket:
                for ind, info in pocket['body'].items():
                    slot = self.form.get_comp_by_name("us" + ind)
                    if info:
                        slot.username = info['username']
                        slot.play_count = info['play_count']
                    else:
                        slot.username = ""
                    slot.update_render()

            sleep(20)
    
    def send_data(self, pocket):
        t = pocket['type']
        if t == "chat_message":
            self.chat.text += pocket['body'] + "\n"
            self.chat.text = "\n".join(self.chat.text.split("\n")[-8:])
        if t == "lobby_player_join":
            self.new_player(pocket)
        if t == "lobby_player_leave":
            self.player_left(pocket)

    def send_message(self):
        msg = self.chat_edit.text
        self.net.send(ChatMessage(msg))
        self.chat_edit.text = ""

    def new_player(self, pocket: dict):
        slot = self.form.get_comp_by_name("us" + str(self.players))
        if not slot:
            print("[LOBBY] uh um there is too many players, lobby can't handle more than 5 players sorry xd")
            return
        slot.username = pocket['body']['username']
        slot.play_count = pocket['body']['play_count']
        slot.update_render()
        self.players += 1
    
    def player_left(self, pocket: dict):
        for comp in self.form.components:
            try:
                if comp.username == pocket['body']['username']:
                    comp.username = ""    
                    comp.update_render()
                    self.players -= 1
                    break
            except AttributeError:
                continue

    def draw(self) -> None:
        scr = self.screen
        scr.fill(0)
        scr.blit(self.form.render(), [0, 0])
        draw.line(scr, (255, 255, 255), (0, scr.get_height() * 0.65), (scr.get_width(), scr.get_height() * 0.65), 2)
    
    def update(self, events):
        self.form.update(events)