import pygame


FONT = None


def init():
    """Initialize font for PygameUI"""
    global FONT
    FONT = pygame.font.SysFont('Arial', 20)


def is_hover(mouse_loc, rect):
    """Check to see if the mouse collides with a rect"""
    rect: pygame.Rect or (float or int, float or int, float or int, float or int)
    mouse_loc: (float or int, float or int)
    rect = rect if type(rect) == pygame.Rect else pygame.Rect(rect)
    if rect.x < mouse_loc[0] < rect.x+rect.width:
        if rect.y < mouse_loc[1] < rect.y+rect.height:
            return True
    return False


def extend_rect(rect, amount):
    """Extend a Pygame Rect outwards in all directions by a specified amount"""
    rect: pygame.Rect
    rect = rect.copy()
    rect.x -= amount
    rect.y -= amount
    rect.width += amount*2
    rect.height += amount*2
    return rect


class Element:
    def __init__(self, rect, color, secondary_color=None):
        rect: (int or float, int or float, int or float, int or float) or (int or float, int or float)
        color: (int or float, int or float, int or float)
        secondary_color: (int or float, int or float, int or float)
        if len(rect) == 2:
            self.rect = pygame.Rect([rect[0], rect[1], 0, 0])
        else:
            self.rect = pygame.Rect(rect)
        self.maincolor = pygame.Color(color)
        if secondary_color is not None:
            self.secondcolor = pygame.Color(secondary_color)
        else:
            self.secondcolor = pygame.Color(255, 255, 255)


class Text(Element):
    def __init__(self, loc, color, text, font=FONT, antialias=True):
        super().__init__(loc, color)
        text: str
        font: pygame.font.Font
        self.text = font.render(text, antialias, self.maincolor)

    def set_text(self, text, font=FONT, antialias=True):
        font: pygame.font
        text: str
        self.text = font.render(text, antialias, self.maincolor)

    def set_color(self, color):
        color: (int or float, int or float, int or float) or pygame.Color
        self.maincolor = pygame.Color(color)

    def draw(self, screen):
        screen: pygame.Surface
        screen.blit(self.text, self.rect)

    def get_surface(self):
        return self.text

    def get(self):
        return self


class Button(Element):
    def __init__(self, rect, color, action, font=FONT, text="", secondcolor=(0, 0, 0), antialias=True, actionargs=None):
        super().__init__(rect, color)
        self.action = action
        self.secondcolor = secondcolor
        self.text = font.render(text, antialias, self.secondcolor)
        self.lmbstate = False
        self.clicked = False
        self.actionargs = actionargs

    def set_text(self, text, font=FONT, antialias=True):
        font: pygame.font
        text: str
        self.text = font.render(text, antialias, self.secondcolor)

    def set_color(self, color):
        color: (int or float, int or float, int or float) or pygame.Color
        self.maincolor = pygame.Color(color)

    def set_secondcolor(self, secondcolor):
        secondcolor: (int or float, int or float, int or float) or pygame.Color
        self.secondcolor = pygame.Color(secondcolor)

    def draw(self, screen, border_rounding=5):
        screen: pygame.Surface
        self.text: pygame.Surface
        pygame.draw.rect(screen, self.secondcolor, self.rect, border_radius=border_rounding)
        pygame.draw.rect(screen, self.maincolor, extend_rect(self.rect, -2), border_radius=border_rounding)
        screen.blit(self.text, self.text.get_rect(center=self.rect.center))

    def register_clicks(self):
        oldlmb = self.lmbstate
        newlmb = pygame.mouse.get_pressed(3)[0]
        if is_hover(pygame.mouse.get_pos(), self.rect):
            self.clicked = not oldlmb and newlmb
            if self.clicked:
                if self.actionargs is not None:
                    if type(self.actionargs) not in [tuple, list]:
                        self.action(*(self.actionargs,))
                    else:
                        self.action(*self.actionargs)
                else:
                    self.action()
        self.lmbstate = newlmb

    def get_surface(self):
        return self.text

    def get(self):
        return self
