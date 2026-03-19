from __future__ import annotations
import pygame
import sys
import time
import random


FPS = 30
ITERATIONS = 1
G_ORIG = 6.67430 * 10 ** -11
G = G_ORIG * 1000000
# G = 1
colors = [(255, 0, 0), (0, 255, 0),
          (255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 255, 255)]
colors += [(x[0] // 2, x[1] // 2, x[2] // 2) for x in colors]

pygame.init()
pygame.font.init()
random.seed(time.time())

def init_font(font=None):
    if not font:
        font = random.choice(pygame.font.get_fonts())
    return pygame.font.SysFont(font, 48), pygame.font.SysFont(font, 16), font

myfont, myfontsmall, _ = init_font('sourcecodepro')
clock = pygame.time.Clock()

size = width, height = 1280, 840
init_size = size
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
screen = pygame.display.set_mode(size, pygame.NOFRAME)
selected = []
textin = []
status = []
help = '\n    '.join(['commands:', 'global:', *('\n    '.join(['', 'h - help', 'g{number} - multiply gravitational constant G by number', 't{number} - set length of trail', 'i{number} - set number of iterations per tick',
                                                               't - toggle trails', 'c - change color', 'f - change font', 'q / [Esc] - quit', 'f11 - fullscreen'])).split('\n')[1:], 'body:', *('\n    '.join(['', 'm{number} - set mass', 'r{number} - set radius', '[left click] - select body', '[right click] - move body'])).split('\n')[1:]])
mousex, mousey = 0, 0
leftheld, rightheld = False, False
show_trails = True
trail_size = 1000
fullscreen = False

# bodies = init_bodies()
# stars = init_stars()

class Body:
    def __init__(self, x, y, mass, radius, v, color=None) -> None:
        self.x = x
        self.y = y
        self.v = v
        self.m = mass
        self.r = radius
        if not color:
            self.color = random.choice(colors)
        else:
            self.color = color
        self.trail = []
        self.destroyed = False
        self.radial_density = self.m / self.r
        self.dm = 0

    def update(self, body: Body):
        if self.dm < 0:
            pass
            # return self.destory()
        elif self.dm > 0: 
            self.m = self.dm
            dr = self.m / self.radial_density
            # if dr < 1: 
            #     return self.destory()
            self.r = dr
        dx = body.x - self.x
        dy = body.y - self.y
        r2 = dx * dx + dy * dy
        if r2 <= (self.r + body.r) ** 2:
            # self.dm = self.m - body.m
            # self.r = self.radial_density / self.m
            # self.v[0] *= -1
            # self.v[1] *= -1
            pass
        else:
            r3_inv = (r2*r2**0.5)**-1
            a = G * body.m * r3_inv
            # self.a = [a * dx, a * dy]
            self.v[0] += a * dx
            self.v[1] += a * dy
        self.x += self.v[0]
        self.y += self.v[1]

    def destory(self): 
        self.destroyed = True

    def __repr__(self) -> str:
        return f'{self.x} {self.y} {self.m} {self.r}'


CONFIG = {
    'star_with_comets': lambda: [
        Body(width / 1, height / 1, 1000,     6,  [-.1, .1]),
        Body(width / 2, height / 2, 10000000,     10,  [-.1, .1]),
        Body(width / 3, height / 3, 1000,     5,  [-.1, .1]),
        Body(width / 4, height / 4, 1000,       5,  [-.1, .1]),
        Body(width / 5, height / 5, 1000,        1,  [-.1, .1]),
        Body(width / 6, height / 6, 1000,        1,  [-.1, .1]),
        Body(width / 7, height / 7, 1000,        1,  [-.1, .1]),
        Body(width / 8, height / 8, 1000,        1,  [-.1, .1]),
        Body(width / 9, height / 9, 1000,     5,    [-.1, .1])
    ],
    '3stars': lambda: [
        Body(width / 3,   height / 3,   1000000, 10, [0, .3]),
        Body(width / 2,   height / 1.5, 1000000, 10, [.3, 0]),
        Body(width / 1.5, height / 3,   1000000, 10, [-.3, 0]),
        Body(width / 2,   height / 2,   100,    5,  [0, -.3]),
    ]
}

CURRENT_CONFIG = '3stars'


def init_bodies():
    identifier_str = CURRENT_CONFIG
    print(f"config={identifier_str}")
    identifier_str = identifier_str.lower()
    bodyidx = None
    if selected and bodies:
        bodyidx = bodies.index(selected[1])
    if identifier_str not in CONFIG: 
        raise Exception(f'Invalid identifier:  {identifier_str}')
    bdis = CONFIG[identifier_str]()

    if bodyidx:
        selected[0] = time.time()
        selected[1] = bodies[bodyidx]
    return bdis


def init_stars(n=200):
    s = [1, 1.5, 2, 2.5]
    maxs = int(max(s) * 2)
    from itertools import product
    strs = []
    star_colors = [(127, 127, 127), (255, 255, 255),
                   (255, 207, 181), (199, 210, 255)]
    xrange = range(maxs, width - maxs, maxs)
    yrange = range(maxs, height - maxs, maxs)
    positions = list(product(xrange, yrange))
    random.shuffle(positions)
    strs = [Body(*positions[i], 0, random.choice(s), [0, 0],
                 random.choice(star_colors)) for i in range(n)]
    return strs


def process_textin():
    global G, bodies, status
    if len(textin) == 1:
        if textin[0][1].lower() == 'c':
            for body in bodies:
                body.color = random.choice(colors)
        elif textin[0][1].lower() == 't':
            global show_trails
            show_trails = not show_trails
        elif textin[0][1].lower() == 'f':
            global myfont, myfontsmall
            myfont, myfontsmall, _ = init_font()
        elif textin[0][1].lower() == 's': 
            available_configs = list(CONFIG.keys())
            global CURRENT_CONFIG
            CURRENT_CONFIG = available_configs[(available_configs.index(CURRENT_CONFIG)+1)%len(available_configs)]
            bodies = init_bodies()   
        elif textin[0][1].lower() == 'h':
            print(help)
        elif textin[0][1].lower() == 'e':
            bodies = init_bodies()
        else:
            status = [time.time(), red, 'ValueError1']
    elif len(textin) > 1:
        if textin[0][1].lower() == 't':
            try:
                global trail_size
                ts = int(''.join([x[1] for x in textin[1:]]))
                if ts > trail_size:
                    bodies = init_bodies()
                trail_size = ts
            except ValueError as e:
                status = [time.time(), red, str(e)]
        elif textin[0][1].lower() == 'g':
            try:
                print(f"G {G}->", end='')
                G *= float(''.join([x[1] for x in textin[1:]]))
                print(f"{G}")
                bodies = init_bodies()
            except ValueError as e:
                status = [time.time(), red, str(e)]
        elif textin[0][1].lower() == 'i':
            try:
                n = int(''.join([x[1] for x in textin[1:]]))
                if n < 0:
                    raise ValueError('i cant travel back in time')
                global ITERATIONS
                ITERATIONS = n
            except ValueError as e:
                status = [time.time(), red, str(e)]             
        elif textin[0][1].lower() == 'm':
            if selected:
                try:
                    n = int(''.join([x[1] for x in textin[1:]]))
                    if n < 0:
                        raise ValueError('negative mass')
                    selected[1].m = n
                except ValueError as e:
                    status = [time.time(), red, str(e)]
            else:
                status = [time.time(), red, 'no body selected']
        elif textin[0][1].lower() == 'r':
            if selected:
                try:
                    n = int(''.join([x[1] for x in textin[1:]]))
                    if n < 0:
                        raise ValueError('negative radius')
                    selected[1].r = n
                    print(bodies)
                except ValueError as e:
                    status = [time.time(), red, str(e)]
            else:
                status = [time.time(), red, 'no body selected']

        else:
            status = [time.time(), red, 'ValueError2']
    if not status:
        status = [time.time(), white, f" >{''.join([x[1] for x in textin])}"]

    textin.clear()


def iterations(n=1):
    for _ in range(n):
        for body1 in bodies:
            for body2 in bodies:
                if body1 == body2 or body2.destroyed:
                    continue
                body2.update(body1)
        for body in bodies:
            body.trail.append([body.x, body.y])
    for body in bodies:
        body.trail = body.trail[-trail_size:]


print(help)

bodies = init_bodies()
stars =  init_stars()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_RETURN:
                process_textin()
            elif event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(
                        (0, 0), pygame.FULLSCREEN)
                    info = pygame.display.Info()
                    size = width, height = info.current_w, info.current_h
                else:
                    screen = pygame.display.set_mode(init_size, pygame.NOFRAME)
                    size = width, height = init_size
                bodies = init_bodies()
                stars = init_stars()
            elif event.key == pygame.K_BACKSPACE:
                if textin:
                    textin = textin[:-1]
                    if textin:
                        textin[-1][0] = time.time()
            elif event.key in [pygame.K_TAB, pygame.K_LALT, pygame.K_RALT]:
                pass
            else:
                textin.append([time.time(), event.unicode])
        if event.type == pygame.QUIT:
            sys.exit()

    mousex, mousey = pygame.mouse.get_pos()
    left, middle, right = pygame.mouse.get_pressed(3)
    if left:
        if not leftheld:
            for body in bodies:
                if mousex > body.x - body.r and mousex < body.x + body.r:
                    if mousey > body.y - body.r and mousey < body.y + body.r:
                        selected = [time.time(), body]
                        break
            else:
                selected.clear()
        leftheld = True
    else:
        leftheld = False
    if right:
        if rightheld:
            if selected:
                selected[1].x = mousex
                selected[1].y = mousey
        rightheld = True
    else:
        rightheld = False

    clock.tick(FPS)

    iterations(ITERATIONS)

    screen.fill(black)

    for star in stars:
        pygame.draw.circle(screen, star.color, (star.x, star.y), star.r)

    for body in bodies:
        if not body.destroyed:
            pygame.draw.circle(screen, body.color, (body.x, body.y), body.r)
            if selected:
                if body == selected[1]:
                    pygame.draw.circle(screen, body.color,
                                        (body.x, body.y), body.r + 3, 1)
        if show_trails:
            for point in body.trail:
                pygame.draw.circle(screen, body.color,
                                   (point[0], point[1]), 1)

    if selected:
        body: Body = selected[1]
        x, y = body.x + body.r, body.y + body.r
        texts = [f'x: {round(body.x, 2)}  y: {round(body.y, 2)}',
                 f'mass: {body.m}', f'radius: {body.r}']
        textsizes = [myfontsmall.size(x) for x in texts]
        boxwidth, boxheight = max([x[0] for x in textsizes]), sum(
            [x[1] for x in textsizes])
        pygame.draw.rect(screen, (125, 125, 125),
                         (x, y, boxwidth, boxheight), 0)
        j = 0
        for text in texts:
            text1 = myfontsmall.render(
                text, True, white)
            screen.blit(text1, (x, y + textsizes[j][1] * j))
            j += 1

    if textin:
        # if time.time() - textin[-1][0] > 4:
        #     process_textin()
        textsurface = myfont.render(
            ''.join([x[1] for x in textin]), True, white)
        screen.blit(textsurface, (0, 0))

    if status:
        if time.time() - status[0] < 1.5:
            errortext = myfontsmall.render(status[2], True, status[1])
            screen.blit(errortext, (0, myfont.get_height()))
        else:
            status.clear()

    fpstext = myfontsmall.render(
        f'{round(clock.get_fps(), 2)}', True, white)
    screen.blit(fpstext, (width - myfontsmall.get_height() * 3, 0))
    pygame.display.flip()
