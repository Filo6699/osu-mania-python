from client.scenes.scene_components import Scene, Form, TextEdit, Button, Label
from client.pockets import LoginPocket
from client.network import Network


class Auth(Scene):
    def __init__(self, screen, net: Network, change_scene) -> None:
        super().__init__(screen, change_scene)
        self.net = net
        self.bg_color = (125, 125, 145)
        self.form_offset = [screen.get_width() / 2 - 250, screen.get_height() / 2 - 250]
        self.form = Form((500, 500), self.form_offset)

        self.form.add_component(TextEdit((300, 50), "login_field", [100, 130], 'Enter your login'))

        pwd_field = TextEdit((300, 50), "password_field", [100, 200], 'Enter your password')
        pwd_field.password_style = True
        self.form.add_component(pwd_field)

        button = Button("Log in", (300, 50), "login_button", [100, 300])
        button.on_click = self.login_click
        self.form.add_component(button)

        button = Button("Register", (300, 50), "register_button", [100, 370])
        button.on_click = self.register_click
        self.form.add_component(button)

        self.warning = Label("", [300, 0], "warning", [self.form.sizes[0] / 2, 90])
        self.warning.color = (255, 0, 0)
        self.form.add_component(self.warning)

    def login_click(self):
        login = self.form.get_comp_by_name('login_field')
        pwd = self.form.get_comp_by_name('password_field')

        llen = len(login.text)
        if llen < 4 or llen > 20:
            self.form.set_focus(login)
            self.warning.text = "Login must be 4-20 characters"
            return

        llen = len(pwd.text)
        if llen < 4 or llen > 20:
            self.form.set_focus(pwd)
            self.warning.text = "Password must be 4-20 characters"
            return

        if not self.net.send(LoginPocket(login.text, pwd.text)):
            self.warning.text = "Wasn't able to connect to the server"
    
    def send_data(self, data: dict):
        if data['correct'] == False:
            self.warning.text = "Wrong login or password"
    
    def register_click(self):
        self.change_scene('register')

    def draw(self) -> None:
        scr = self.screen
        scr.fill(0)
        scr.blit(self.form.render(), self.form_offset)
    
    def update(self, events):
        self.form.update(events)
