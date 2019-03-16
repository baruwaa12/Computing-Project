import math
import os
from random import randint
from collections import deque 

import pygame
from pygame.locals import *

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 200, 0)
bright_green = (0, 180, 0)
bright_red = (230, 0, 0)

# Appropriate music to be found and played.z
# PLAY BACKGROUND MUSIC
# pygame.mixer_music.load("")
# pygame.mixer_music.set_volume(0.5)
# pygame.mixer_music.play(-1)


FPS = 60
ANIMATION_SPEED = 0.18  # pixels per millisecond
WIN_WIDTH = 284 * 2
WIN_HEIGHT = 512
display_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
clock = pygame.time.Clock()


class Bird(pygame.sprite.Sprite):
    # Attributes:
    # x: The bird's X coordinate
    # y: The bird's Y coordinate
    # millisecond_to_climb: milliseconds left during a climb, where a complete climb lasts Bird.Climb_Duration

    # Constants:
    # WIDTH: The width, in pixels, of the bird's image.
    # HEIGHT: The height, in pixels, of the bird's image.
    # SINK_SPEED: the speed at which the bird descends in pixels per millisecond
    # CLIMB_SPEED: the speed at which the bird ascends in one second while climbing on average
    # CLIMB_DURATION: the number of milliseconds to execute a single climb.

    WiDTH = HEIGHT = 32
    SINK_SPEED = 0.18
    CLIMB_SPEED = 0.3
    CLIMB_DURATION = 333.3

    def __init__(self, x, y, millisecond_to_climb, images):

        super(Bird, self).__init__()
        self.x, self.y = x, y
        self.millisecond_to_climb = millisecond_to_climb
        self._img_wing_up, self._img_wing_down = images
        self._mask_wing_up = pygame.mask.from_surface(self._img_wing_up)
        self._mask_wing_down = pygame.mask.from_surface(self._img_wing_down)

    def update(self, delta_frames=1):
        # This function updates the bird's position
        # This function uses the cosine function to achieve a smooth climb:
        # Arguments: delta_frames the number of frames elasped since this method was last called.

        if self.millisecond_to_climb > 0:
            fraction_climb_done = 1 - self.millisecond_to_climb/Bird.CLIMB_DURATION
            self.y -= (Bird.CLIMB_SPEED * frames_to_millisecond(delta_frames) *
                       (1 - math.cos(fraction_climb_done * math.pi)))
            self.millisecond_to_climb -= frames_to_millisecond(delta_frames)
        else:
            self.y += Bird.SINK_SPEED * frames_to_millisecond(delta_frames)

    @property
    def image(self):
        if pygame.time.get_ticks() % 500 >= 250:
            return self._img_wing_up
        else:
            return self._img_wing_down

    @property
    def mask(self):
        if pygame.time.get_ticks() % 500 >= 250:
            return self._mask_wing_up
        else:
            return self._mask_wing_down

    @property
    def rect(self):
        return Rect(self.x, self.y, Bird.WiDTH, Bird.HEIGHT)


class PipePair(pygame.sprite.Sprite):

    # Represents an obstacle.

    # A PipePair has a top and a bottom pipe, and only between them can the bird pass -- if it collides with either part
    # the game will end

    # Attributes
    # x = The PipePair's X position. This is a float to make movement smoother. Note that there is no y attribute,
    #  as it will only ever be 0.
    # image: A pygame.Surface which can be blitted to the main surface
    # to display the PipePair.
    # mask: A bitmask which excludes all pixels in self.image with a transparency greater than 127. helps detection
    # top_pieces : THe number of pieces, including the end piece, in top pipe.
    # bottom_pieces: The number of pieces, including the end piece, the bottom pipe.

    # Constants:
    # WIDTH: The width of the pipe in
    # PIECE_HEIGHT: The height of the pipe piece in pixels
    # ADD_INTERVAL: The interval, in milliseconds, in between adding new pipes.

    WIDTH = 80
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 3000

    def __init__(self, pipe_end_img, pipe_body_img):

        # The new PipePair will automatically be assigned an x attribute of WIN_WIDTH
        # top_pieces - The number of pieces which make up the top pipe.
        # bottom_pieces - The number of pieces which make up the bottom pipe.

        self.x = float(WIN_WIDTH - 1)
        self.score_counted = False

        self.image = pygame.Surface((PipePair.WIDTH, WIN_HEIGHT), SRCALPHA)
        self.image.convert()
        self.image.fill((0, 0, 0, 0))
        total_pipe_body_pieces = int(
            (WIN_HEIGHT -
             3 * Bird.HEIGHT -
             3 * PipePair.PIECE_HEIGHT) /
            PipePair.PIECE_HEIGHT
        )
        self.bottom_pieces = randint(1, total_pipe_body_pieces)
        self.top_pieces = total_pipe_body_pieces - self.bottom_pieces

    # bottom pipe
        for i in range(1, self.bottom_pieces + 1):
            piece_pos = (0, WIN_HEIGHT - i * PipePair.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, piece_pos)
            bottom_pipe_end_y = WIN_HEIGHT - self.bottom_pieces
            bottom_end_piece_pos = (0, bottom_pipe_end_y - PipePair.PIECE_HEIGHT)
            self.image.blit(pipe_end_img, bottom_end_piece_pos)

    # top pipe
        for i in range(self.top_pieces):
            self.image.blit(pipe_body_img, (0, i * PipePair.PIECE_HEIGHT))
        top_pipe_end_y = self.top_pieces
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))

    # compensate for added end pieces
        self.top_pieces += 1
        self.bottom_pieces += 1

    # for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_height_px(self):
        return self.top_pieces * PipePair.PIECE_HEIGHT

    @property
    def bottom_height_px(self):
        return self.bottom_pieces * PipePair.PIECE_HEIGHT

    @property
    def visible(self):
        return -PipePair.WIDTH < self.x < WIN_WIDTH

    def update(self, delta_frames=1):
        self.x -= ANIMATION_SPEED * frames_to_millisecond(delta_frames)

    @property
    def rect(self):
        return Rect(self.x, 0, PipePair.WIDTH, PipePair.PIECE_HEIGHT)

    def collides_with(self, bird, pipe):
        return pygame.sprite.collide_mask(bird, pipe)


def load_images():
    # Load all images required by the game and return a dict of them.

    def load_image(img_file_name):
        file_name = os.path.join('.', 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert()
        return img

    return {'background': load_image('background.png'),
            'pipe-end': load_image('pipe_end.png'),
            'pipe-body': load_image('pipe_body.png'),
            'bird_wing_up': load_image('bird_wing_up.png'),
            'bird_wing_down': load_image('bird_wing_down.png')
            }


def frames_to_millisecond(frames, fps=FPS):
    return 1000.0 * frames / fps


def millisecond_to_frames(milliseconds, fps=FPS):
    return fps * milliseconds / 1000.0


def text_objects(text, font):
    text_surface = font.render(text, True, black)
    return text_surface, text_surface.get_rect()


def game_intro():

    pygame.init()
    intro = True

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        display_surface.fill(white)

        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = text_objects("A bit Racey", largeText)
        TextRect.center = ((WIN_WIDTH/2),(WIN_HEIGHT/2))
        display_surface.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(15)


def main():
    # The application's entry point

    # pygame.init()

    pygame.display.set_caption('Pygame Flappy Bird')
    score_font = pygame.font.SysFont(None, 32, bold=True)
    images = load_images()

    # def message_display(text):
    #     large_text = pygame.font.Font('freesansbold.ttf', 115)
    #     text_surf, text_rect = text_objects(text, large_text)
    #     text_rect.center = ((WIN_WIDTH/2), (WIN_HEIGHT/2))
    #     display_surface.blit(text_surf, text_rect)
    #
    #     pygame.display.update()

    # the bird stays in the same x position, so bird_x is a constant
    # center bird on screen
    bird = Bird(50, int(WIN_HEIGHT/2 - Bird.HEIGHT/2), 2,
                (images['bird_wing_up'], images['bird_wing_down']))

    pipes = deque()

    frame_clock = 0
    score = 0
    done = paused = False
    while not done:
        clock.tick(FPS)

        if not (paused or frame_clock % millisecond_to_frames(PipePair.ADD_INTERVAL)):
            pp = PipePair(images['pipe-end'], images['pipe-body'])
            pipes.append(pp)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
                paused = not paused
            elif e.type == MOUSEBUTTONUP or (e.type == KEYUP and
                    e.key in (K_UP, K_RETURN, K_SPACE)):
                bird.millisecond_to_climb = Bird.CLIMB_DURATION

        if paused:
            continue  # don't draw anything
        pipe_collision = any(p.collides_with(bird, p) for p in pipes)
        if pipe_collision or 0 >= bird.y or bird.y >= WIN_HEIGHT - Bird.HEIGHT:
            done = True

        for x in (0, WIN_WIDTH / 2):
            display_surface.blit(images['background'], (x, 0))

        while pipes and not pipes[0].visible:
            pipes.popleft()

        for p in pipes:
            p.update()
            display_surface.blit(p.image, p.rect)

        bird.update()
        display_surface.blit(bird.image, bird.rect)

        # Pending menu screen
        # mouse = pygame.mouse.get_pos
        #
        # if 150+100 > mouse[0] > 150 and 450+50 > mouse[1] > 450:
        #     pygame.draw.rect(display_surface, bright_green, (150,450,100,50))
        # else:
        #     pygame.draw.rect(display_surface, green, (150,450,100,50))
        #
        # if 150+100 > mouse[0] > 150 and 450+50 > mouse[1] > 450:
        #     pygame.draw.rect(display_surface, bright_red, (450, 450, 100, 40))

        # update and display the score
        for p in pipes:
            if p.x + PipePair.WIDTH < bird.x and not p.score_counted:
                score += 1
                p.score_counted = True

        score_surface = score_font.render(str(score), True, (255, 255, 255))
        score_x = WIN_WIDTH/2 - score_surface.get_width()/2
        display_surface.blit(score_surface, (score_x, PipePair.PIECE_HEIGHT))

        pygame.display.flip()
        frame_clock += 1
    print('Game over! Score: %i' % score)
    # game_intro()
    pygame.quit()


if __name__ == '__main__':
    game_intro()
    main()
