import pygame
import sys
from pygame.locals import *


class Display:
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BACKGROUND = (255, 255, 255)
    # Screen information
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 480
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

    def __init__(self):
        pygame.init()
        self.DISPLAYSURF = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.DISPLAYSURF.fill(self.BACKGROUND)
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        pygame.display.set_caption("Tasks")
        # CREATING TASKBUBBLES
        self.taskBoxes = []
        for side in [self.BUBBLE_FROM_LEFT, self.BUBBLE_FROM_RIGHT]:
            for box in range(0, 5):
                self.taskBoxes.append(self.TaskBubble(side, self.BUBBLE_SPACING + box * self.VERTICAL_SPACING))

    def run(self, mods: list, statuses: dict):
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()
        self.DISPLAYSURF.fill(self.BACKGROUND)
        for task in range(0, 10):
            mod: str = mods[task]
            if statuses[mod]:
                self.taskBoxes[task].image.fill(self.GREEN)
            else:
                self.taskBoxes[task].image.fill(self.RED)
            text = self.font.render(mod, True, self.BLACK)
            if task < 5:
                self.DISPLAYSURF.blit(text, (self.TEXT_FROM_LEFT, self.TEXT_SPACING + task * self.VERTICAL_SPACING))
            else:
                self.DISPLAYSURF.blit(text,(self.TEXT_FROM_RIGHT, self.TEXT_SPACING + (task - 5) * self.VERTICAL_SPACING))

        self.draw_boxes()
        for i in range(0, 10): self.taskBoxes[i].draw(self.DISPLAYSURF)

    def draw_boxes(self):
        pygame.draw.rect(self.DISPLAYSURF, self.BLACK, (self.DIST_FROM_LEFT, self.TOP_MARGIN, self.WIDTH, self.HEIGHT),
                         self.BORDER)
        pygame.draw.rect(self.DISPLAYSURF, self.BLACK, (self.DIST_FROM_RIGHT, self.TOP_MARGIN, self.WIDTH, self.HEIGHT),
                         self.BORDER)
        for side in [self.DIST_FROM_LEFT, self.DIST_FROM_RIGHT]:
            for i in range(1, 5):
                pygame.draw.rect(self.DISPLAYSURF, self.BLACK, (side, (i * self.VERTICAL_SPACING + self.TOP_MARGIN),
                                                                self.WIDTH, self.HEIGHT), self.BORDER)
