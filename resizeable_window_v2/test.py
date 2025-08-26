import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plastic Sorting Game")

# Load background image
background = pygame.image.load("background_ocean.jpg").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font setup
title_font = pygame.font.SysFont(None, 64)
sub_font = pygame.font.SysFont(None, 36)

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the background
    screen.blit(background, (0, 0))

    # Draw title text
    title_text = title_font.render("Plastic Sorting Game", True, (255, 255, 255))
    sub_text = sub_font.render("by Jayden Lal", True, (255, 255, 255))

    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
    screen.blit(sub_text, sub_text.get_rect(center=(SCREEN_WIDTH // 2, 110)))

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
