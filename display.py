import pygame
import sys
from pygame.locals import *

pygame.init()

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (255, 255, 255)

# Screen information
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(BACKGROUND)
pygame.display.set_caption("Tasks")

# BOXES
WIDTH = 335
HEIGHT = 80
TOP_MARGIN = 13
VERTICAL_SPACING = TOP_MARGIN + HEIGHT
SIDE_MARGIN = 50
DIST_FROM_LEFT = SIDE_MARGIN
DIST_FROM_RIGHT = SCREEN_WIDTH - WIDTH - SIDE_MARGIN
BORDER = 2

# TEXT
TEXT_MARGIN = 80
TEXT_FROM_LEFT = DIST_FROM_LEFT + TEXT_MARGIN
TEXT_FROM_RIGHT = DIST_FROM_RIGHT + TEXT_MARGIN
TEXT_SPACING = TOP_MARGIN + 25

# TASK BUBBLE
BUBBLE_MARGIN = 40
BUBBLE_FROM_LEFT = DIST_FROM_LEFT + BUBBLE_MARGIN
BUBBLE_FROM_RIGHT = DIST_FROM_RIGHT + BUBBLE_MARGIN
BUBBLE_SPACING = TOP_MARGIN + 40


class TaskBubble(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("RedRectangle.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# -------relevent functions? from FRC716DemoBot--------
# def Controls_init():
# def eventHandler():
# def Stopped():
# def Running():

# def loopDrive():
# def shooter():
# use d-pad to run seperate modules
# CONTROLLER_BUTTON_DPAD_DOWN: int
# CONTROLLER_BUTTON_DPAD_LEFT: int
# CONTROLLER_BUTTON_DPAD_RIGHT: int
# CONTROLLER_BUTTON_DPAD_UP: int
# need list of modules
# list displayed where? - same as tasks on display?
# if so need to figure out how to traverse and then run module
# -----------------------end---------------------------

# CREATING TASKBUBBLES
# column 1
TB1 = TaskBubble(BUBBLE_FROM_LEFT, BUBBLE_SPACING)
TB2 = TaskBubble(BUBBLE_FROM_LEFT, BUBBLE_SPACING + VERTICAL_SPACING)
TB3 = TaskBubble(BUBBLE_FROM_LEFT, BUBBLE_SPACING + 2 * VERTICAL_SPACING)
TB4 = TaskBubble(BUBBLE_FROM_LEFT, BUBBLE_SPACING + 3 * VERTICAL_SPACING)
TB5 = TaskBubble(BUBBLE_FROM_LEFT, BUBBLE_SPACING + 4 * VERTICAL_SPACING)
# column 2
TB6 = TaskBubble(BUBBLE_FROM_RIGHT, BUBBLE_SPACING)
TB7 = TaskBubble(BUBBLE_FROM_RIGHT, BUBBLE_SPACING + VERTICAL_SPACING)
TB8 = TaskBubble(BUBBLE_FROM_RIGHT, BUBBLE_SPACING + 2 * VERTICAL_SPACING)
TB9 = TaskBubble(BUBBLE_FROM_RIGHT, BUBBLE_SPACING + 3 * VERTICAL_SPACING)
TB10 = TaskBubble(BUBBLE_FROM_RIGHT, BUBBLE_SPACING + 4 * VERTICAL_SPACING)

while True:
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # maybe change to touchscreen, would you use mouse coordinates?
    # or implemnt based on dictionary status instead of pressed key
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_1]:
        TB1.image.fill(GREEN)
    if pressed_keys[K_2]:
        TB2.image.fill(GREEN)
    if pressed_keys[K_3]:
        TB3.image.fill(GREEN)
    if pressed_keys[K_4]:
        TB4.image.fill(GREEN)
    if pressed_keys[K_5]:
        TB5.image.fill(GREEN)
    if pressed_keys[K_6]:
        TB6.image.fill(GREEN)
    if pressed_keys[K_7]:
        TB7.image.fill(GREEN)
    if pressed_keys[K_8]:
        TB8.image.fill(GREEN)
    if pressed_keys[K_9]:
        TB9.image.fill(GREEN)
    if pressed_keys[K_0]:
        TB10.image.fill(GREEN)

    DISPLAYSURF.fill(BACKGROUND)

    # TEXT - could prob do more efficiently ehehe
    font = pygame.font.Font('freesansbold.ttf', 32)
    # column 1
    text = font.render('autoPickup', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_LEFT, TEXT_SPACING))
    text = font.render('autoShoot', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_LEFT, TEXT_SPACING + VERTICAL_SPACING))
    text = font.render('driveForward10', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_LEFT, TEXT_SPACING + 2 * VERTICAL_SPACING))
    text = font.render('gyroTurn', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_LEFT, TEXT_SPACING + 3 * VERTICAL_SPACING))
    text = font.render('holdStill', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_LEFT, TEXT_SPACING + 4 * VERTICAL_SPACING))
    # column 2
    text = font.render('TASK 6', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_RIGHT, TEXT_SPACING))
    text = font.render('TASK 7', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_RIGHT, TEXT_SPACING + VERTICAL_SPACING))
    text = font.render('TASK 8', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_RIGHT, TEXT_SPACING + 2 * VERTICAL_SPACING))
    text = font.render('TASK 9', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_RIGHT, TEXT_SPACING + 3 * VERTICAL_SPACING))
    text = font.render('TASK 10', True, BLACK)
    DISPLAYSURF.blit(text, (TEXT_FROM_RIGHT, TEXT_SPACING + 4 * VERTICAL_SPACING))

    # DRAWING RECTANGULAR BOXES
    # column 1
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_LEFT, TOP_MARGIN, WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_LEFT, (VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_LEFT, (2 * VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_LEFT, (3 * VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_LEFT, (4 * VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)
    # column 2
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_RIGHT, TOP_MARGIN, WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_RIGHT, (VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_RIGHT, (2 * VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_RIGHT, (3 * VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)
    pygame.draw.rect(DISPLAYSURF, BLACK, (DIST_FROM_RIGHT, (4 * VERTICAL_SPACING + TOP_MARGIN), WIDTH, HEIGHT), BORDER)

    TB1.draw(DISPLAYSURF)
    TB2.draw(DISPLAYSURF)
    TB3.draw(DISPLAYSURF)
    TB4.draw(DISPLAYSURF)
    TB5.draw(DISPLAYSURF)

    TB6.draw(DISPLAYSURF)
    TB7.draw(DISPLAYSURF)
    TB8.draw(DISPLAYSURF)
    TB9.draw(DISPLAYSURF)
    TB10.draw(DISPLAYSURF)

    # --------from FRC716 Demo Bot-----------
    # time.sleep(0.001)
# Controls_init()
# eventHandler()
# Running()
# Stopped()
# ----------------end---------------------

# -------------scratch & non important notes------------

# import pygame
# from pygame.locals import *
# import sys

# pygame.init()

# BLACK = pygame.Color(0, 0, 0)         
# WHITE = pygame.Color(255, 255, 255)   
# GREY = pygame.Color(128, 128, 128)   
# RED = pygame.Color(255, 0, 0)   
# GREEN = pygame.Color(0, 255, 0)    

# DISPLAYSURF = pygame.display.set_mode((300,300))
# DISPLAYSURF.fill(WHITE)
# pygame.display.set_caption("Example")

# pygame.draw.line(DISPLAYSURF, GREY, (150,130), (130,170))
# pygame.draw.line(DISPLAYSURF, GREY, (150,130), (170,170))
# pygame.draw.line(DISPLAYSURF, GREEN, (130,170), (170,170))
# pygame.draw.circle(DISPLAYSURF, BLACK, (100,50), 30)
# pygame.draw.circle(DISPLAYSURF, BLACK, (200,50), 30)
# pygame.draw.rect(DISPLAYSURF, RED, (100, 200, 100, 50), 2)
# pygame.draw.rect(DISPLAYSURF, BLACK, (110, 260, 80, 5))

# while True:
#     pygame.display.update()
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             pygame.quit()
#             sys.exit()

# while True:
#     events()
#     loop()
#     render()

# pygame.draw.polygon(surface, color, pointlist, width)
# pygame.draw.line(surface, color, start_point, end_point, width)
# pygame.draw.lines(surface, color, closed, pointlist, width)
# pygame.draw.circle(surface, color, center_point, radius, width)
# pygame.draw.ellipse(surface, color, bounding_rectangle, width)
# pygame.draw.rect(surface, color, rectangle_tuple, width)

# ----------------------------end------------------------------------
