import pygame
import sys
import random  # ADDED: for random block positions
import os # for keeping track of highscore

# Freeplay high score
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read().strip() or 0)
else:
    high_score = 0

# Levels highest points
if os.path.exists("highest_level_points.txt"):
    with open("highest_level_points.txt", "r") as f:
        highest_level_points = int(f.read().strip() or 0)
else:
    highest_level_points = 0

# Initialize Pygame
pygame.init()

# Music and Sound
pygame.mixer.init()
effect_sound = pygame.mixer.Sound("effect.mp3")
effect_sound.set_volume(0.3)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
button_color = (0, 100, 200)
button_fill_color = (0, 100, 200)
button_border_color = (100, 150, 255)
BIN_COLOR = (255, 200, 0)
floating_texts = []
BIN_SPEED = 1  # pixels per frame
BLOCK_WIDTH = 40
BLOCK_HEIGHT = 40
BLOCK_COLOR = (200, 200, 255)
BLOCK_SPEED = 1 # must be >1
SPAWN_DELAY = 60  # frames (60fps = 1 second)
CONVEYOR_HEIGHT = 20
BIN_WIDTH = 60
BIN_HEIGHT = 60
MAX_BINS = 3 # max of 8
HINT_DURATION_FRAMES = 180  # ~3 seconds at 60 FPS
# extra block constants for levels mode
BASE_BLOCK_SPEED = 1
BASE_SPAWN_DELAY = 60
SPEED_INCREMENT = 0.3
SPAWN_DECREMENT = 5 

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plastic Collector Game")

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

# Add mode and level variables
game_mode = None  # None, "levels", or "freeplay"
current_level = 1
level_score_goal = 5000
level_lives = 3

# Home screen buttons
play_levels_text = button_font.render("Play (Levels)", True, (255,255,255))
play_levels_rect = play_levels_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
free_play_text = button_font.render("Free Play", True, (255,255,255))
free_play_rect = free_play_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))

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

# Placeholder block data
falling_blocks = []  # list of pygame.Rect
spawn_timer = 0
clock = pygame.time.Clock()

# Drag and drop plastic text
show_hint = False
hint_timer = 0

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
paused = False
game_started = False

running = True
while running:
    clock.tick(60)  # limit to 60fps

    # Event handling
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not on_title_screen:
                paused = not paused
            
        if on_title_screen and event.type == pygame.MOUSEBUTTONDOWN:
            if play_levels_rect.collidepoint(event.pos):
                game_mode = "levels"
                lives = 3
                current_level = 1
                on_title_screen = False
                show_hint = True
                hint_timer = HINT_DURATION_FRAMES
                game_started = True
            elif free_play_rect.collidepoint(event.pos):
                game_mode = "freeplay"
                lives = 6
                on_title_screen = False
                show_hint = True
                hint_timer = HINT_DURATION_FRAMES
                game_started = True

        elif not on_title_screen and not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                # Check if clicked on any block
                for block_dict in reversed(falling_blocks):  # Topmost block gets priority
                    block = block_dict["rect"]
                    if block.collidepoint(event.pos):
                        dragging_block = block_dict  # store the whole dict, not just rect
                        show_hint = False  # hide hint immediately when player interacts
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
        title_text = title_font.render("Plastic Collector Game", True, (255, 255, 255))
        sub_text = sub_font.render("by Jayden Lal", True, (255, 255, 255))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
        screen.blit(sub_text, sub_text.get_rect(center=(SCREEN_WIDTH // 2, 110)))

        # Draw buttons with fill and border
        for rect in [play_levels_rect, free_play_rect]:
            pygame.draw.rect(screen, button_fill_color, rect.inflate(20, 10))      # fill
            pygame.draw.rect(screen, button_border_color, rect.inflate(20, 10), 3) # border

        # Draw text on top of buttons
        screen.blit(play_levels_text, play_levels_rect)
        screen.blit(free_play_text, free_play_rect)

    elif game_over:
        # Game over screen
        screen.fill((0, 0, 0))
        
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        
        if game_mode == "freeplay":
            score_text = hud_font.render(f"Final Score: {points}", True, (255, 255, 255))
            high_score_text = hud_font.render(f"High Score: {high_score}", True, (255, 255, 255))
            score_y = SCREEN_HEIGHT // 2 - 10
            level_reached_y = SCREEN_HEIGHT // 2 + 30  # placeholder for hint positioning
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, score_y))
            screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, level_reached_y))
        else:  # levels mode
            score_text = hud_font.render(f"Final Score: {points}", True, (255, 255, 255))
            highest_level_text = hud_font.render(f"Highest Level Points: {highest_level_points}", True, (255, 255, 255))
            level_reached_text = hud_font.render(f"Game Ended on Level {current_level}", True, (255, 255, 255))

            score_y = SCREEN_HEIGHT // 2 - 10
            highest_level_y = SCREEN_HEIGHT // 2 + 30
            level_reached_y = SCREEN_HEIGHT // 2 + 70

            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, score_y))
            screen.blit(highest_level_text, (SCREEN_WIDTH // 2 - highest_level_text.get_width() // 2, highest_level_y))
            screen.blit(level_reached_text, (SCREEN_WIDTH // 2 - level_reached_text.get_width() // 2, level_reached_y))

        # Press SPACE hint
        hint_text = hud_font.render("Press SPACE to continue", True, (200, 200, 200))
        hint_y = level_reached_y + 40  # always 40px below the last text
        screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, hint_y))
        
        pygame.display.flip()

        # Wait for space to continue
        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_space = False
    
        reset_game()


    else:
        # Gameplay screen
        
        # Pause screen
        if paused and game_started:
            pause_text = hud_font.render("PAUSED", True, (255, 255, 0))
            screen.blit(pause_text,
                        (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                         SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))
            pygame.display.flip()
            continue

        # Spawn blocks every SPAWN_DELAY frames
        spawn_timer += 1
        if spawn_timer >= SPAWN_DELAY:
            x = random.randint(0, SCREEN_WIDTH - BLOCK_WIDTH)
            # 10% chance for special plastic
            # Increase special plastic chance with level
            special_chance = min(0.1 + (current_level - 1) * 0.05, 0.5)  # caps at 50%
            block_type = "special" if random.random() < special_chance else "normal"
            falling_blocks.append({"rect": pygame.Rect(x, -BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT), "type": block_type})
            spawn_timer = 0

        # Update and draw blocks
        for block_dict in falling_blocks[:]:
            block = block_dict["rect"]

            if block_dict != dragging_block:
                # faster special plastic
                if block_dict["type"] == "special":
                    block.y += block_speed * 1.7 # 70% faster for special plastic
                else:
                    block.y += block_speed # normal speed

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
                    effect_sound.play()
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

        # Current level modifiers
        if game_mode == "levels":
            block_speed = BASE_BLOCK_SPEED + (current_level - 1) * SPEED_INCREMENT
            spawn_delay = max(10, BASE_SPAWN_DELAY - (current_level - 1) * SPAWN_DECREMENT)
        else:
            block_speed = BLOCK_SPEED
            spawn_delay = SPAWN_DELAY

        # Level progression (if on levels)
        if game_mode == "levels" and points >= current_level * level_score_goal:
            current_level += 1
            lives += 3  # give 3 more lives for next level
            
        # Only write highscore in freeplay    
        if game_mode == "freeplay" and points > high_score:
            high_score = points
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))

        # Only write levels highest points in levels mode
        if game_mode == "levels" and points > highest_level_points:
            highest_level_points = points
            with open("highest_level_points.txt", "w") as f:
                f.write(str(highest_level_points))

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

        # Show the temporary hint at the start of a game
        if show_hint:
            hint_text = hud_font.render("Use mouse to drag and drop plastic, p to pause.", True, (255, 255, 255))
            hint_bg = pygame.Surface((hint_text.get_width() + 20, hint_text.get_height() + 10))
            hint_bg.set_alpha(120)  # subtle translucent background
            hint_bg.fill((0, 0, 0))
            hint_x = (SCREEN_WIDTH - hint_bg.get_width()) // 2
            hint_y = 110  # under the title area; adjust if you like
            screen.blit(hint_bg, (hint_x, hint_y))
            screen.blit(hint_text, (hint_x + 10, hint_y + 5))

            hint_timer -= 1
            if hint_timer <= 0:
                show_hint = False
                
        # Show current level only in Levels mode
        if game_mode == "levels":
            level_text = hud_font.render(f"Level: {current_level}", True, (255, 255, 255))
            screen.blit(level_text, (10, 70))
        elif game_mode == "freeplay":
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
