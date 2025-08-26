import pygame
import sys
import random  # ADDED: for random block positions
import os # for keeping track of highscore

# Load high score from file
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read().strip() or 0)
else:
    high_score = 0

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_WIDTH = 40
BLOCK_HEIGHT = 40
BLOCK_COLOR = (200, 200, 255)
BLOCK_SPEED = 1
SPAWN_DELAY = 60  # frames (60fps = 1 second)
CONVEYOR_HEIGHT = 20
BIN_WIDTH = 60
BIN_HEIGHT = 60
MAX_BINS = 3
bin_color = (255, 200, 0)
floating_texts = []

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
hud_font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)
font_float = pygame.font.SysFont(None, 36)

# Game state
on_title_screen = True

# Score system
points = 0
lives = 6

# Button setup
button_text = button_font.render("Play", True, (255, 255, 255))
button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
button_color = (0, 100, 200)

# Generate bins at random positions
def spawn_bins():
    bins = []
    used_positions = []
    while len(bins) < MAX_BINS:
        x = random.randint(0, SCREEN_WIDTH - BIN_WIDTH)
        # avoid overlapping bins too much
        if all(abs(x - ux) > BIN_WIDTH for ux in used_positions):
            used_positions.append(x)
            bin_rect = pygame.Rect(x, SCREEN_HEIGHT - CONVEYOR_HEIGHT - BIN_HEIGHT, BIN_WIDTH, BIN_HEIGHT)
            bins.append(bin_rect)
    return bins

bins = spawn_bins()
BIN_SPEED = 1  # pixels per frame

# Placeholder block data
falling_blocks = []  # list of pygame.Rect
spawn_timer = 0
clock = pygame.time.Clock()

# Drag and drop state
dragging_block = None
drag_offset_x = 0
drag_offset_y = 0

game_over = False  # Flag to control game over state

# ADDED: function to reset game
def reset_game():
    global falling_blocks, spawn_timer, points, lives, bins, on_title_screen, game_over
    falling_blocks = []
    spawn_timer = 0
    points = 0
    lives = 6
    bins = spawn_bins()
    on_title_screen = True
    game_over = False

# Load images
plastic_img = pygame.image.load("plastic.png").convert_alpha()
special_plastic_img = pygame.image.load("special_plastic.png").convert_alpha()
special_plastic_img = pygame.transform.scale(special_plastic_img, (BLOCK_WIDTH, BLOCK_HEIGHT))
bin_img = pygame.image.load("bin.png").convert_alpha()

# Resize images if needed
plastic_img = pygame.transform.scale(plastic_img, (BLOCK_WIDTH, BLOCK_HEIGHT))
bin_img = pygame.transform.scale(bin_img, (BIN_WIDTH, BIN_HEIGHT))  # adjust BIN_WIDTH & BIN_HEIGHT


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

        elif not on_title_screen and not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                # Check if clicked on any block
                for block_dict in reversed(falling_blocks):  # Topmost block gets priority
                    block = block_dict["rect"]
                    if block.collidepoint(event.pos):
                        dragging_block = block_dict  # store the whole dict, not just rect
                        drag_offset_x = event.pos[0] - block.x
                        drag_offset_y = event.pos[1] - block.y
                        break
                    
            elif event.type == pygame.MOUSEMOTION and dragging_block:
                # Update block position
                dragging_block["rect"].x = event.pos[0] - drag_offset_x
                dragging_block["rect"].y = event.pos[1] - drag_offset_y

            # let go of plastic    
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_block = None

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

    elif game_over:
        # Game over screen
        screen.fill((0, 0, 0)) # clear screen
        
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        score_text = hud_font.render(f"Final Score: {points}", True, (255, 255, 255))
        high_score_text = hud_font.render(f"High Score: {high_score}", True, (255, 255, 255))

        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()
        pygame.time.wait(2000)  # wait 2 seconds

        # Update high score if beaten
        if points > high_score:
            high_score = points
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))

        # Reset game
        reset_game()


    else:
        # Gameplay screen

        # Spawn blocks every SPAWN_DELAY frames
        spawn_timer += 1
        if spawn_timer >= SPAWN_DELAY:
            x = random.randint(0, SCREEN_WIDTH - BLOCK_WIDTH)
            # 10% chance for special plastic
            block_type = "special" if random.random() < 0.1 else "normal"
            falling_blocks.append({"rect": pygame.Rect(x, -BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT), "type": block_type})
            spawn_timer = 0

        # Update and draw blocks
        for block_dict in falling_blocks[:]:
            block = block_dict["rect"]

            if block_dict != dragging_block:
                # faster special plastic
                if block_dict["type"] == "special":
                    block.y += BLOCK_SPEED* 1.7 # 70% faster for special plastic
                else:
                    block.y += BLOCK_SPEED # normal speed

            # draw plastic (different image for special)
            if block_dict["type"] == "special":
                screen.blit(special_plastic_img, (block.x, block.y)) #  special image
            else:
                screen.blit(plastic_img, (block.x, block.y))

        # Check for block-bin collisions
        for block_dict in falling_blocks[:]:
            block = block_dict["rect"]
            for bin_rect in bins:
                if block.colliderect(bin_rect):
                    if block_dict["type"] == "special":
                        points += 250
                        floating_texts.append([font_float.render("+250", True, (255, 215, 0)), bin_rect.centerx, bin_rect.top - 20, 20])
                    else:
                        points += 100
                        floating_texts.append([font_float.render("+100", True, (255, 255, 0)), bin_rect.centerx, bin_rect.top - 20, 20])
                    falling_blocks.remove(block_dict)
                    break # Stop checking other bins for this block

            # Lose life if block falls off screen
            if block.y > SCREEN_HEIGHT and block != dragging_block:
                falling_blocks.remove(block_dict)
                lives -= 1
                if lives <= 0:
                    game_over = True  # Trigger game over

        # Update and draw bins
        for i, bin_rect in enumerate(bins):
            bin_rect.x -= BIN_SPEED
            if bin_rect.right < 0:
                # Respawn on right
                bin_rect.x = SCREEN_WIDTH
            screen.blit(bin_img, (bin_rect.x, bin_rect.y))

        # Draw HUD
        points_text = hud_font.render(f"Points: {points}", True, (255, 255, 255))
        lives_text = hud_font.render(f"Lives: {lives}", True, (255, 255, 255))
        screen.blit(points_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        high_score_text = hud_font.render(f"High Score: {high_score}", True, (255, 255, 255))
        screen.blit(high_score_text, (10, 70))

        # Draw floating texts
        for text in floating_texts[:]:
            screen.blit(text[0], (text[1], text[2]))
            text[2] = text[2]  # stays still, no float
            text[3] -= 1       # countdown timer
            if text[3] <= 0:
                floating_texts.remove(text)

    # Update display
    pygame.display.flip()

# Quit
pygame.quit()
sys.exit()
