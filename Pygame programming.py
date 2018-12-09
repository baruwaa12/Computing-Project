# Description
import pygame

pygame.init()

display_width = 960
display_height = 540

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('A bit Racey')
clock = pygame.time.Clock()

bgImg = pygame.image.load('city.gif')
x = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

    relative_x = x % bgImg.get_rect(). width
    gameDisplay.blit(bgImg, (relative_x - bgImg.get_rect(). width, 0))
    if relative_x < display_width:
        gameDisplay.blit(bgImg, (relative_x, 0))
    x -= 1

    pygame.display.update()
    clock.tick(60)
