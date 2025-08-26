import pygame
import sys
import random  # ADDED: for random block positions

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_WIDTH = 40
BLOCK_HEIGHT = 40
BLOCK_COLOR = (200, 200, 255)
BLOCK_SPEED = 1.5
SPAWN_DELAY = 60  # frames (60fps = 1 second)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plastic Sorting Game")

# Load background image
background = pygame.image.load("background_ocean.jpg").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font setup
title_font = pygame.font.SysFont(None, 64)
sub_font = pygame.font.SysFont(None, 36)
button_font = pygame.font.SysFont(None, 48)

# Game state
on_title_screen = True

# Button setup
button_text = button_font.render("Play", True, (255, 255, 255))
button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
button_color = (0, 100, 200)

# Placeholder block data
falling_blocks = []  # list of pygame.Rect
spawn_timer = 0
clock = pygame.time.Clock()

# Drag and drop state
dragging_block = None
drag_offset_x = 0
drag_offset_y = 0

# Game loop
running = True
while running:
    clock.tick(60)  # limit to 60fps

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if on_title_screen and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                on_title_screen = False  # Switch to gameplay screen

        elif not on_title_screen:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicked on any block
                for block in reversed(falling_blocks):  # Topmost block gets priority
                    if block.collidepoint(event.pos):
                        dragging_block = block
                        drag_offset_x = event.pos[0] - block.x
                        drag_offset_y = event.pos[1] - block.y
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_block = None

            elif event.type == pygame.MOUSEMOTION and dragging_block:
                # Update block position
                dragging_block.x = event.pos[0] - drag_offset_x
                dragging_block.y = event.pos[1] - drag_offset_y

    # Draw the background
    screen.blit(background, (0, 0))

    if on_title_screen:
        # Draw title text
        title_text = title_font.render("Plastic Sorting Game", True, (255, 255, 255))
        sub_text = sub_font.render("by Jayden Lal", True, (255, 255, 255))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
        screen.blit(sub_text, sub_text.get_rect(center=(SCREEN_WIDTH // 2, 110)))

        # Play button background
        pygame.draw.rect(screen, button_color, button_rect.inflate(20, 10))
        screen.blit(button_text, button_rect)
    else:
        # Gameplay screen

        # Spawn blocks every SPAWN_DELAY frames
        spawn_timer += 1
        if spawn_timer >= SPAWN_DELAY:
            x = random.randint(0, SCREEN_WIDTH - BLOCK_WIDTH)
            falling_blocks.append(pygame.Rect(x, -BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT))
            spawn_timer = 0

        # Update and draw blocks
        for block in falling_blocks:
            if block != dragging_block:
                block.y += BLOCK_SPEED
            pygame.draw.rect(screen, BLOCK_COLOR, block)

        # Remove blocks that fell off screen (but not if dragging)
        falling_blocks = [b for b in falling_blocks if b.y < SCREEN_HEIGHT or b == dragging_block]

    # Update display
    pygame.display.flip()

# Quit
pygame.quit()
sys.exit()
