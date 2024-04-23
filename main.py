import random
import pygame
from game import GameState
from pregenerator import load_world
from worldgen import elevation_to_rgba

def get_landscape_surface(game: GameState):
    pygame_surface = pygame.surfarray.make_surface(game.world.world_color[:, :, :3])
    return pygame_surface

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("My Pygame Program")

landscape_surf = get_landscape_surface()

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game logic

    # Render graphics
    screen.fill((0, 0, 0))  # Fill the screen with black
    # Add your drawing code here

    screen.blit(landscape_surf, (0, 0))

    pygame.display.flip()  # Update the display

# Quit Pygame
pygame.quit()