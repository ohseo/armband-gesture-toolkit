import matplotlib
matplotlib.use('module://pygame_matplotlib.backend_pygame')
import matplotlib.pyplot as plt

import pygame
import pygame.display

fig, axes = plt.subplots(1, 1,)
axes.plot([1,2], [1,2], color='green', label='test')

fig.canvas.draw()

screen = pygame.display.set_mode((800, 600))

# Use the fig as a pygame.Surface
screen.blit(fig, (0,0))

show = True
while show:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Stop showing when quit
            show = False
    pygame.display.update()