from pygame import Surface, draw, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, SRCALPHA, MOUSEMOTION
from pygame.font import Font


def load_fonts() -> None:
    fsize = 36
    default_font = Font(None, fsize)
    TextEdit.font_size = fsize * (4/3)
    TextEdit.input_font = default_font
    TextEdit.error_font = Font(None, fsize)
    TextEdit.error_font.set_underline(1)

    Button.label_font = default_font
    # fsize = 30
    Label.label_font = default_font

    fsize = 27
    Map.hover_font = Font(None, fsize)

    Slot.font = default_font


def render_hover_info(text: str, font: Font) -> Surface:
    lines = text.split("\n")
    rendered = []
    max_len = [0, 0]
    height = 0
    for l in lines:
        r = font.render(l, 1, (222, 222, 222))
        rendered.append(r)
        sz = r.get_size()
        height += sz[1]
        max_len = [
            max(max_len[0], sz[0]),
            max(max_len[1], sz[1]),
        ]
    margin_y = 0
    sur = Surface((
        max_len[0] + 10,
        margin_y * (len(rendered) - 1) + height + 10
    ), flags=SRCALPHA)
    draw.rect(sur, (13, 13, 13), (0, 0, *sur.get_size()), border_radius=8)
    draw.rect(sur, (222, 222, 222), (0, 0, *sur.get_size()), 1, border_radius=8)
    offset_y = 0
    for ind, lin in enumerate(rendered):
        sur.blit(lin, (5, 5 + ind * margin_y + offset_y))
        offset_y += lin.get_height()
    return sur


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
        self.hover_pos = False
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
        self.color = (15, 15, 15)
        self.is_pressed = False
        self.pressed_color = (43, 43, 43)
        self.border_radius = 10
        self.outline_color = (255, 255, 255)
        self.outline_width = 1
    
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
        draw.rect(surface, self.outline_color, (*self.pos, *self.sizes), width=self.outline_width, border_radius=self.border_radius)

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
        self.color = (80, 80, 80)
        self.error_color = (140, 80, 80)
        self.error = False
        self.border_radius = 5
        self.symbol_limit = 20
        self.password_style = False
    
    def enter_pressed(self): ...
    
    def set_focus(self):
        self.focus = True
        self.error = False
    
    def keyinput(self, key: str):
        if key == b'\x08'.decode():
            if len(self.text) > 0:
                self.text = self.text[:-1]
        elif key == b'\r'.decode():
            self.enter_pressed()
        elif key == "space":
            self.text += " "
        elif not key.isprintable():
            return
        elif len(key) == 1:
            self.text += key

        if len(self.text) >= self.symbol_limit:
            self.text = self.text[:self.symbol_limit]
    
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
        renders = []
        max_len = 0
        for line in self.text.split("\n"):
            r = self.label_font.render(line, 1, self.color)
            renders.append(r)
            max_len = max(max_len, r.get_width())
        offsety = 0
        for line in renders:
            if self.is_centered:
                pos = [
                    self.pos[0] - line.get_width() / 2,
                    self.pos[1] + offsety
                ]
            else:
                pos = [self.pos[0], self.pos[1] + offsety]
            surface.blit(line, pos)
            offsety += line.get_height() + 2
        

class Map(Component):
    hover_font: Font = None

    def __init__(self, sizes, name: str, position: list = [0, 0], is_hidden=False) -> None:
        super().__init__(sizes, name, position, is_hidden)
        # self.map_info
        self.hover_text = "info\nfewfewfweff\n\n\nf"
    
    def draw(self, surface: Surface):
        if self.hover_pos:
            surface.blit(render_hover_info(self.hover_text, self.hover_font), self.hover_pos)


class Slot(Component):
    font: Font = None

    def __init__(self, username, pl_count, sizes, name: str, position: list = [0, 0], is_hidden=False) -> None:
        super().__init__(sizes, name, position, is_hidden)
        self.username = username
        self.play_count = pl_count
        self.render = None
        self.update_render()
    
    def update_render(self) -> None:
        sr = Surface(self.sizes, flags=SRCALPHA)
        draw.rect(sr, (70, 70, 70, 100), (0, 0, *self.sizes))
        if self.username:
            usn = self.font.render(self.username, 1, (255, 255, 255))
            pl = self.font.render(str(self.play_count), 1, (255, 255, 255))
            usn_pos = [
                8,
                self.sizes[1] / 2 - usn.get_height() / 2
            ]
            pl_pos = [
                self.sizes[0] - 8 - pl.get_width(),
                self.sizes[1] / 2 - pl.get_height() / 2
            ]
            sr.blit(usn, usn_pos)
            sr.blit(pl, pl_pos)
        self.render = sr

    def draw(self, surf: Surface):
        ren = self.render.copy()
        if self.hover_pos:
            ren.fill((200, 200, 200), special_flags=3)
        surf.blit(ren, self.pos)


class Form:
    def __init__(self, sizes=(500, 500), offset=(0, 0)) -> None:
        self.sizes = sizes
        self.offset = offset
        self.bg_color = (25, 25, 25)
        self.components = []
        self.focus = None
        self.border_radius = 25
        self.last_clicked = None
        self.border_color = (255, 255, 255)
    
    def add_component(self, component: Component):
        self.components.append(component)
    
    def get_comp_by_name(self, name: str):
        for c in self.components:
            if c.name == name:
                return c
        return None
    
    def render(self) -> Surface:
        out = Surface(self.sizes, SRCALPHA)
        out.fill((255, 255, 255, 0))
        draw.rect(out, self.bg_color, (0, 0, *self.sizes), border_radius=self.border_radius)
        draw.rect(out, self.border_color, (0, 0, *self.sizes), 2, border_radius=self.border_radius)
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
            if e.type == MOUSEMOTION:
                e.pos = [
                    e.pos[0] - self.offset[0],
                    e.pos[1] - self.offset[1],
                ]
                for comp in self.components:
                    xdi = e.pos[0] - comp.pos[0]
                    ydi = e.pos[1] - comp.pos[1]
                    if xdi > 0 and xdi < comp.sizes[0] and ydi > 0 and ydi < comp.sizes[1]:
                        comp.hover_pos = e.pos
                    else:
                        comp.hover_pos = None
