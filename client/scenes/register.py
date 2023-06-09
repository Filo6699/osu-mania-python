from client.scenes.scene_components import Scene, Form, TextEdit, Button, Label
from client.pockets import RegisterPocket
from client.network import Network


class Register(Scene):
    def __init__(self, screen, net: Network, change_scene) -> None:
        super().__init__(screen, change_scene)
        self.net = net
        self.bg_color = (125, 125, 145)
        self.form_offset = [screen.get_width() / 2 - 250, screen.get_height() / 2 - 250]
        self.form = Form((500, 500), self.form_offset)

        self.login = TextEdit((300, 50), "login_field", [100, 120], 'Enter your login')
        self.form.add_component(self.login)

        self.username = TextEdit((300, 50), "username_field", [100, 190], 'Enter your username')
        self.form.add_component(self.username)

        self.password = TextEdit((300, 50), "password_field", [100, 260], 'Enter your password')
        self.password.password_style = True
        self.form.add_component(self.password)

        button = Button("Register", (300, 50), "register_button", [100, 380])
        button.on_click = self.register_click
        self.form.add_component(button)

        button = Button("back", (60, 30), "back_button", [225, 450])
        button.on_click = self.back_click
        self.form.add_component(button)

        self.warning = Label("", [300, 0], "warning", [100, 100])
        self.warning.color = (255, 50, 50)
        self.form.add_component(self.warning)
    
    def send_data(self, data: dict):
        if data['correct'] == False:
            self.warning.text = "This login is already in use"
    
    def back_click(self):
        self.change_scene("auth")

    def register_click(self):
        for c in [self.login, self.username, self.password]:
            llen = len(c.text)
            if llen < 4 or llen > 20:
                self.form.set_focus(c)
                match c.name:
                    case "login_field":
                        piece = "Login"
                    case "username_field":
                        piece = "Username"
                    case "password_field":
                        piece = "Password"
                self.warning.text = piece + " must be 4-20 characters"
                return
        
        self.net.send(RegisterPocket(self.login.text, self.username.text, self.password.text))

    def draw(self) -> None:
        scr = self.screen
        scr.fill(0)
        scr.blit(self.form.render(), self.form_offset)
    
    def update(self, events):
        self.form.update(events)
