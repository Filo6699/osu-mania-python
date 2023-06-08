from pygame import Surface, draw, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, key, SRCALPHA
from pygame.font import Font


def load_fonts() -> None:
    fsize = 36
    TextEdit.font_size = fsize * (4/3)
    TextEdit.input_font = Font(None, fsize)
    TextEdit.error_font = Font(None, fsize)
    TextEdit.error_font.set_underline(1)

    Button.label_font = Font(None, fsize)
    # fsize = 30
    Button.label_font.set_bold(1)
    Label.label_font = Font(None, fsize)


class Scene:
    def __init__(self, screen: Surface, change_scene) -> None:
        self.screen = screen
        self.change_scene = change_scene

    def send_data(self, data: dict): ...
    def draw(self) -> None: ...
    def update(self, events) -> None: ...

class Component:
    def __init__(self, sizes, name: str, position: list=[0, 0], is_hidden=False) -> None:
        self.sizes = sizes
        self.hidden = is_hidden
        self.focus = False
        self.pos = position
        self.name = name
    
    def set_focus(self):
        self.focus = True
    
    def draw(self, surface: Surface) -> None: ...

class Button(Component):
    label_font: Font = None

    def __init__(self, label: str, sizes, name: str, position: list = [0, 0], is_hidden=False) -> None:
        super().__init__(sizes, name, position, is_hidden)
        self.label = label
        self.color = (200, 200, 215)
        self.is_pressed = False
        self.pressed_color = (170, 170, 185)
        self.border_radius = 13
    
    def on_click(self): ...
    def on_unclick(self): ...

    def click(self, _):
        self.on_click()
        self.is_pressed = True
    
    def unclick(self, _):
        self.on_unclick()
        self.is_pressed = False

    def draw(self, surface: Surface):
        if self.is_pressed:
            color = self.pressed_color
        else:
            color = self.color
        draw.rect(surface, color, (*self.pos, *self.sizes), border_radius=self.border_radius)

        clr = [
            255 - color[0],
            255 - color[1],
            255 - color[2],
        ]
        rnd = self.label_font.render(self.label, 1, clr)
        pos = [
            self.pos[0] + self.sizes[0] / 2 - rnd.get_width() / 2,
            self.pos[1] + self.sizes[1] / 2 - rnd.get_height() / 2,
        ]
        surface.blit(rnd, pos)

class TextEdit(Component):
    input_font: Font = None
    error_font: Font = None
    font_size: int = None

    def __init__(self, sizes, name: str, position: list=[0, 0], ghost_text: str="", is_hidden=False) -> None:
        sizes = [
            max(sizes[0], self.font_size * 2),
            max(sizes[1], self.font_size + 2),
        ]
        super().__init__(sizes, name, position, is_hidden)
        self.text = ""
        self.margin = (self.sizes[1] - self.font_size / 2) / 2
        self.ghost_text = ghost_text
        self.color = (80, 80, 100)
        self.error_color = (140, 80, 100)
        self.error = False
        self.border_radius = 5
        self.symbol_limit = 20
        self.password_style = False
    
    def set_focus(self):
        self.focus = True
        self.error = False
    
    def keyinput(self, key: str):
        if key == b'\x08'.decode():
            if len(self.text) > 0:
                self.text = self.text[:-1]
        elif key == "space":
            self.text += " "
        elif not key.isprintable():
            return
        elif len(key) == 1:
            self.text += key

        if len(self.text) >= self.symbol_limit:
            self.text = self.text[:20]
    
    def draw(self, surface: Surface):
        if self.error:
            color = self.error_color
        else:
            color = self.color
        
        if self.focus:
            color = (
                max(color[0] - 15, 0),
                max(color[1] - 15, 0),
                max(color[2] - 15, 0),
            )

        draw.rect(surface, color, (*self.pos, *self.sizes), border_radius=self.border_radius)

        if self.error:
            font = self.error_font
            color = (255, 55, 25)
        else:
            font = self.input_font

        if self.text:
            if self.password_style:
                text = '*'*len(self.text)
            else:
                text = self.text
            color = (255, 255, 255)
        else:
            text = self.ghost_text
            color = (160, 160, 160)

        rend = font.render(text, 1, color)
        font_pos = [
            self.pos[0] + self.margin,
            self.pos[1] + self.margin,
        ]
        surface.blit(rend, font_pos)

class Label(Component):
    label_font: Font = None

    def __init__(self, text: str, sizes, name: str, position: list = [0, 0], is_hidden=False) -> None:
        super().__init__(sizes, name, position, is_hidden)
        self.text = text
        self.color = (255, 255, 255)
        self.is_centered = True
    
    def draw(self, surface: Surface):
        rend = self.label_font.render(self.text, 1, self.color)
        if self.is_centered:
            font_pos = [
                self.pos[0] + self.sizes[0] / 2 - rend.get_width() / 2,
                self.pos[1] + self.sizes[1] / 2 - rend.get_height() / 2,
            ]
        else:
            font_pos = self.pos
        surface.blit(rend, font_pos)
        

class Form:
    def __init__(self, sizes=(500, 500), offset=(0, 0)) -> None:
        self.sizes = sizes
        self.offset = offset
        self.bg_color = (125, 125, 145)
        self.components = []
        self.focus = None
        self.border_radius = 25
        self.last_clicked = None
    
    def add_component(self, component: Component):
        self.components.append(component)
    
    def get_comp_by_name(self, name: str):
        for c in self.components:
            if c.name == name:
                return c
    
    def render(self) -> Surface:
        out = Surface(self.sizes, SRCALPHA)
        out.fill((255, 255, 255, 0))
        draw.rect(out, self.bg_color, (0, 0, *self.sizes), border_radius=self.border_radius)
        for comp in self.components:
            comp.draw(out)
        return out

    def set_focus(self, comp):
        self.focus = comp
        for c2 in self.components:
            c2.focus = False
        comp.set_focus()
    
    def update(self, events):
        for e in events:
            if e.type == KEYDOWN:
                try:
                    self.focus.keyinput(e.unicode)
                except AttributeError:
                    continue
            if e.type == MOUSEBUTTONDOWN:
                e.pos = [
                    e.pos[0] - self.offset[0],
                    e.pos[1] - self.offset[1],
                ]
                for comp in self.components:
                    comp: Component
                    xdi = e.pos[0] - comp.pos[0]
                    ydi = e.pos[1] - comp.pos[1]
                    if xdi > 0 and xdi < comp.sizes[0] and ydi > 0 and ydi < comp.sizes[1]:
                        self.set_focus(comp)
                        try:
                            comp.click(e.pos)
                            self.last_clicked = comp
                        except AttributeError:
                            continue
                        break
            if e.type == MOUSEBUTTONUP:
                e.pos = [
                    e.pos[0] - self.offset[0],
                    e.pos[1] - self.offset[1],
                ]
                try:
                    self.last_clicked.unclick(e.pos)
                except AttributeError:
                    continue
