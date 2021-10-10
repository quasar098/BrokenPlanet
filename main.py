import pygame
import pygameui as pygui
from pygameui import is_hover
from os import getcwd as _getdir
from constants import *
from math import pi, cos
from numpy import clip as clamp, floor
from json import loads, dumps
from random import randint as rand
from time import time as unix_time


WIDTH, HEIGHT = 1280, 720
HALFW, HALFH = WIDTH/2, HEIGHT/2
FRAMERATE = 75
pygame.init()
pygui.init()
worlddatasizewhenend = 0
particles = []


def getcwd(file_):
    """Get image through static exe"""
    return _getdir() + file_


def cserp(min_, max_, amount):
    """Like lerp but with cosine instead of linear"""
    return (cos((clamp(amount, 0, 1)*-1+1)*pi)/2+0.5)*(max_-min_)+min_


# noinspection PyUnresolvedReferences
def map_to_json():
    json = {}
    for tile_ in world_data:
        if not tile_.gravity:
            if json.__contains__(str(int(floor((HEIGHT-tile_.y)/32)-1))):
                json[str(int(floor((HEIGHT-tile_.y)/32)-1))].append(floor(tile_.x/32))
            else:
                json[str(int(floor((HEIGHT-tile_.y)/32)-1))] = [floor(tile_.x/32)]
    return json


pygame.mixer.set_num_channels(41)
lose_channel = pygame.mixer.Channel(40)
lose_channel.set_volume(0.2)
lose_sound = pygame.mixer.Sound(getcwd("\\sounds\\lose.wav"))
doing_lose_anim = False

sound_storage = {}
channels = []
for _ in range(2, 30):
    ch = pygame.mixer.Channel(_)
    ch.set_volume(0.2)
    channels.append(ch)


def play_sound(name):
    if not sound_storage.__contains__(name):
        sound_storage[name] = pygame.mixer.Sound(getcwd(name))
    for __ in channels:
        if not __.get_busy():
            __.play(sound_storage[name])
            return


def play_lose_sound():
    lose_channel.play(lose_sound)


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.yvelo = -5
        self.xvelo = rand(-5, 5)
        self.age = rand(6, 12)

    def draw(self, color):
        self.yvelo += 9/FRAMERATE
        self.yvelo = clamp(self.yvelo, -300, 3)
        self.y += self.yvelo
        self.x += self.xvelo
        self.xvelo /= 1 + 1/FRAMERATE
        pygame.draw.circle(screen, color, (self.x, self.y), self.age)
        self.age -= 5/FRAMERATE
        if self.age < 0:
            particles.remove(self)


class Tile:
    def __init__(self, x, y, x2, y2, pyrect):
        pyrect: pygame.Rect
        self.yvelo = -170/FRAMERATE
        self.pyrect = pyrect
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.gravity = False
        self._gravity = False

    def draw(self, surface, texture, shake_=(0, 0), playsound=True):
        surface: pygame.Surface
        texture: pygame.Surface
        surface.blit(texture, texture.get_rect(topleft=(self.x+shake_[0], self.y+shake_[1])))
        if self.gravity and not self._gravity:
            self._gravity = self.gravity
            play_sound("\\sounds\\stone-rumble.mp3") if playsound else None

    def update_rect(self):
        self.pyrect = pygame.Rect(self.x, self.y, 32, 32)


clock = pygame.time.Clock()
screen = pygame.display.set_mode([WIDTH, HEIGHT])
font = pygame.font.Font(getcwd("\\PressStart2P.ttf"), 20)
pygame.display.set_caption("Broken Planet")
pygame.display.set_icon(pygame.image.load(getcwd("\\images\\logo.ico")))
with open(getcwd("\\map.json"), 'r') as file:
    worldmap = loads(file.read())
world_data = []
for qy in worldmap:
    for sx in worldmap[qy]:
        sy = int(qy)
        world_data.append(Tile(sx*32, HEIGHT-sy*32-32, sx*32+32, HEIGHT-sy*32,
                               pygame.Rect(sx*32, HEIGHT-sy*32-32, 32, 32)))

viewpage = "main_menu"
worlddatasize = len(world_data)
when_start = 0
when_end = 0

# main menu stuff
play_now_text = pygui.Text((HALFW-40, HALFH+130), TEXT_COLOR, "PLAY", font=font)
main_menu_logo = pygame.image.load(getcwd("\\images\\mainlogo.png")).convert_alpha()
planet = pygame.image.load(getcwd("\\images\\planetlogo.png")).convert_alpha()
left_half_planet = pygame.transform.scale(pygame.transform.chop(planet, (200, 0, 200, 0)), (100, 200))
right_half_planet = pygame.transform.scale(pygame.transform.chop(planet, (0, 0, 200, 0)), (100, 200))
planet_offset = 0
planet_offset_goal = 0
logo_offset = 0
play_selection_visible = False
debug = False
do_play_sound = True


class Player:
    def __init__(self, x, y, jump_power=5, gravity=10, speed=4):
        self.x = x
        self.y = y
        self.yvelo = 0
        self.xvelo = 0
        self.jump_power = jump_power
        self.gravity = gravity
        self.rect = player_surface.get_rect(midbottom=(self.x, self.y))
        self.speed = speed
        self.isGrounded = True

    def draw(self, surface):
        global worldmap
        surface: pygame.Surface
        self.update_rect()

        # Y CHECKING
        self.isGrounded = False
        self.yvelo += self.gravity * 1/FRAMERATE
        if bool(pygame.Rect(self.rect.x, self.rect.y+self.yvelo,
                            self.rect.w, self.rect.h).collidelist([rect.pyrect for rect in world_data])+1):
            self.yvelo = 0

        if bool(pygame.Rect(self.rect.x, self.rect.y+self.rect.h,
                            self.rect.w, 3).collidelist([rect.pyrect for rect in world_data])+1):
            self.isGrounded = True

        self.y += self.yvelo
        if self.isGrounded:
            for falltile in world_data:
                if pygame.Rect(self.rect.x, self.rect.y+self.rect.h, self.rect.w, 3).colliderect(falltile.pyrect):
                    falltile.gravity = True

        # X CHECKING
        if bool(pygame.Rect(self.rect.x+self.xvelo, self.rect.y+3,
                            self.rect.w, self.rect.h-6).collidelist([rect.pyrect for rect in world_data])+1):
            self.xvelo = 0
        self.x += self.xvelo

        surface.blit(player_surface, self.rect)

    def update_rect(self):
        self.rect = player_surface.get_rect(midbottom=(self.x, self.y))

    def collision(self, worldrects=None):
        self.update_rect()
        if worldrects is None:
            worldrects = [rect.pyrect for rect in world_data]
        return bool(self.rect.collidelist(worldrects)+1)

    def jump(self):
        if self.isGrounded:
            self.yvelo = -self.jump_power
            self.isGrounded = False

    def move(self, direction, decline=False):
        self.xvelo += direction * self.speed * 15/FRAMERATE
        self.xvelo = clamp(self.xvelo, -300/FRAMERATE, 300/FRAMERATE)
        if decline:
            self.xvelo /= 1 + 15/FRAMERATE


# game stuff
ground_surface = pygame.image.load(getcwd("\\images\\ground.png")).convert_alpha()
player_surface = pygame.image.load(getcwd("\\images\\player.png")).convert_alpha()
player_surface = pygame.transform.scale(player_surface, (18, 31))
player = Player(HALFW, HALFH)
parallax = []
tile = Tile(0, 0, 0, 0, (0, 0, 0, 0))
score = 0


def go_back():
    global viewpage, play_selection_visible, logo_offset, player, doing_lose_anim, do_play_sound
    viewpage = "main_menu"
    play_selection_visible = False
    player = Player(HALFW, HALFH)
    logo_offset = 0
    doing_lose_anim = False
    do_play_sound = True


# you lose
gobacktomenu = pygui.Button((HALFW-100, HALFH+40, 200, 50), OTHER_COLOR, go_back, text="Main Menu", font=font,
                            secondcolor=TEXT_COLOR)
scoretext = pygui.Text((HALFW, HALFH-40), TEXT_COLOR, "your score: ", font=font)

running = True
while running:
    screen.fill(BG_COLOR)
    mouseLoc = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if is_hover(mouseLoc, planet.get_rect(midtop=(HALFW, HALFH+40))) and not play_selection_visible:
                    play_selection_visible = True
            if viewpage == "game":
                if debug:
                    if event.button == 3:
                        tile = Tile(int(floor(mouseLoc[0]/32)*32),
                                    int(floor((mouseLoc[1]+16)/32)*32-16),
                                    int(floor(mouseLoc[0]/32)*32)+32,
                                    int(floor((mouseLoc[1]+16)/32)*32-16),
                                    # pyrect below
                                    pygame.Rect(int(floor(mouseLoc[0]/32)*32),
                                                int(floor((mouseLoc[1]+16)/32)*32-16),
                                                32, 32))
                        if not len([tile for tile in world_data if tile.x == int(floor(mouseLoc[0]/32)*32)
                                    and tile.y == int(floor((mouseLoc[1]+16)/32)*32-16)]) == 1:
                            world_data.append(tile)
                    elif event.button == 1:
                        if world_data.__contains__(tile):
                            world_data.remove(tile)
        if event.type == pygame.KEYDOWN:
            if viewpage == "game":
                if event.key == pygame.K_F11:
                    debug = not debug
                    player.gravity = 0 if debug else 10
                    player.yvelo = 0
                if event.key == pygame.K_s:
                    if debug:
                        print(dumps(map_to_json()))

    # code go here
    if viewpage == "main_menu":
        planet_offset_goal += 1/FRAMERATE if play_selection_visible else -2/FRAMERATE
        planet_offset_goal = clamp(planet_offset_goal, 0, 1)
        planet_offset = cserp(0, 800, planet_offset_goal)
        screen.blit(main_menu_logo, (0, -cserp(0, HEIGHT, logo_offset)))
        screen.blit(left_half_planet, left_half_planet.get_rect(topright=(HALFW-planet_offset, HALFH+40)))
        screen.blit(right_half_planet, left_half_planet.get_rect(topleft=(HALFW+planet_offset, HALFH+40)))
        play_now_text.draw(screen) if not play_selection_visible else None
        logo_offset += 1/FRAMERATE if play_selection_visible and planet_offset >= 700 else -1/FRAMERATE
        logo_offset = clamp(logo_offset, 0, 1)
        if logo_offset > 0:
            viewpage = "game"
            when_start = unix_time()

    elif viewpage == "game":
        # player
        if not debug:
            player.move(0, True)
            if pygame.key.get_pressed()[RIGHT]:  # move right
                player.move(1)
            if pygame.key.get_pressed()[LEFT]:  # move left
                player.move(-1)
            for key in JUMP_BUTTON:
                if pygame.key.get_pressed()[key]:
                    player.jump()

        if rand(1, FRAMERATE*5) == 1:
            parallax.append([pygame.Rect(-3123, rand(100, HEIGHT-100), rand(40, 400), 900),
                             pygame.Color(rand(170, 240), rand(1, 56), rand(177,  255)), -156, rand(50, 180)/FRAMERATE])
        for cube in parallax:
            # noinspection PyTypeChecker
            psurface = pygame.Surface(cube[0][2:])
            pygame.draw.rect(psurface, cube[1], cube[0])
            cube[0].x = cube[2]
            cube[2] += cube[3]
            psurface.set_alpha(20)
            screen.blit(psurface, cube[0])

        player.draw(screen)

        # grounds drawing
        for drawtile in world_data:
            shake = 0, 0
            if drawtile.gravity:
                drawtile.yvelo += player.gravity/FRAMERATE
                shake = rand(-2, 2), rand(-2, 2)
                if drawtile.yvelo > 0:
                    drawtile.y += drawtile.yvelo * 75/FRAMERATE
                    drawtile.update_rect()

            drawtile.draw(screen, ground_surface, shake, playsound=do_play_sound)
            if drawtile.y > HEIGHT:  # destroy if off screen
                for i in range(5):
                    particles.append(Particle(drawtile.x, drawtile.y))
                world_data.remove(drawtile)

        for particle in particles:
            particle.draw((255, 136, 23))

        if logo_offset != 1:  # draw logo anim when starting
            screen.blit(main_menu_logo, (0, -cserp(0, HEIGHT, logo_offset)))
            logo_offset += 1/FRAMERATE if play_selection_visible and planet_offset >= 700 else 0
            logo_offset = clamp(logo_offset, 0, 1)

        if player.y > HEIGHT:  # when lose am i right chat
            if not doing_lose_anim:
                do_play_sound = False
                worlddatasizewhenend = len(world_data)
                play_lose_sound()
                for losetile in world_data:
                    losetile.gravity = True
                    losetile.yvelo = -rand(100, 300)/FRAMERATE
                doing_lose_anim = True
            if doing_lose_anim and not lose_channel.get_busy():
                viewpage = "you_lose"
                when_end = unix_time()
                score = int(worlddatasize/(worlddatasizewhenend+1)*1000-(when_end-when_start)*10-900)
                scoretext.set_text(f'your score: {score}', font=font)
                for qy in worldmap:
                    for sx in worldmap[qy]:
                        sy = int(qy)
                        world_data.append(Tile(sx*32, HEIGHT-sy*32-32, sx*32+32, HEIGHT-sy*32,
                                               pygame.Rect(sx*32, HEIGHT-sy*32-32, 32, 32)))
    elif viewpage == "you_lose":
        screen.fill((0, 0, 0))
        gobacktomenu.draw(screen)
        gobacktomenu.register_clicks()
        screen.blit(scoretext.text, scoretext.text.get_rect(center=scoretext.rect[:2]))
        # todo: add ranks: pro gamer, skilled gamer, normal gamer, newb gamer, n00b gamer, afk nerd

    clock.tick(75)
    pygame.display.flip()
pygame.quit()

# todo: add more sounds + sound system
