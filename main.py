import random
import pygame
import os
from pathlib import Path
from pygame import mixer

# ----------------------------
# Config
# ----------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_Y = 525
PLAYER_SPEED = 320.0        # px/sec
ROCKET_SPEED = 650.0        # px/sec
ENEMY_SPEED = 140.0         # px/sec
ENEMY_DROP = 40             # px each edge bounce
NUM_ENEMIES = 12

COLLISION_RADIUS = 27
COLLISION_RADIUS_SQ = COLLISION_RADIUS * COLLISION_RADIUS

WHITE = (255, 255, 255)

BASE_DIR = Path(__file__).parent

bg_music = None
music_started = False

# ----------------------------
# Helpers
# ----------------------------
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def is_collision(ex, ey, rx, ry):
    dx = ex - rx
    dy = ey - ry
    return (dx * dx + dy * dy) < COLLISION_RADIUS_SQ


def asset(*path):
    return BASE_DIR.joinpath(*path)
# ----------------------------
# Init
# ----------------------------
pygame.init()
mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Assets
background = pygame.image.load(asset("assets", "background.jpg")).convert()
player_img = pygame.image.load(asset("assets", "player.png")).convert_alpha()
enemy_img = pygame.image.load(asset("assets", "alien.png")).convert_alpha()
rocket_img = pygame.image.load(asset("assets", "bullet.png")).convert_alpha()
icon = pygame.image.load(asset("assets", "ufo.png")).convert_alpha()


# Sounds (load once!)
if not music_started:
    bg_music = mixer.Sound(asset("audio", "game_background.wav"))
    bg_music.set_volume(0.5)
    bg_music.play(loops=-1)
    music_started = True


rocket_sound = mixer.Sound(asset("audio", "laser.wav"))
explosion_sound = mixer.Sound(asset("audio", "explosion.wav"))


# Fonts
font = pygame.font.Font("freesansbold.ttf", 32)
over_font = pygame.font.Font("freesansbold.ttf", 64)

# Player state
player_x = 370.0
player_y = float(PLAYER_Y)
player_vx = 0.0

# Score
score_value = 0
textX, textY = 10, 10

# Rocket state
rocket_x = 0.0
rocket_y = 480.0
rocket_state = "ready"  # "ready" or "fire"

# Enemy state (store as floats where needed)
enemies = []
for _ in range(NUM_ENEMIES):
    enemies.append({
        "x": float(random.randint(0, WIDTH - 65)),
        "y": float(random.randint(50, 150)),
        "vx": ENEMY_SPEED,   # px/sec (sign = direction)
    })

# ----------------------------
# Draw functions
# ----------------------------
def draw_score():
    score_surf = font.render(f"Score : {score_value}", True, WHITE)
    screen.blit(score_surf, (textX, textY))

def draw_game_over():
    over_surf = over_font.render(f"GAME OVER : {score_value}", True, WHITE)
    screen.blit(over_surf, (200, 250))

def draw_player(x, y):
    screen.blit(player_img, (x, y))

def draw_enemy(x, y):
    screen.blit(enemy_img, (x, y))

def draw_rocket(x, y):
    # Slight offset to center it relative to player like your original
    screen.blit(rocket_img, (x + 16, y + 10))

# ----------------------------
# Game loop
# ----------------------------
running = True
game_over_flag = False

while running:
    dt = clock.tick(FPS) / 1000.0  # seconds since last frame

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_vx = -PLAYER_SPEED
            elif event.key == pygame.K_RIGHT:
                player_vx = PLAYER_SPEED
            elif event.key == pygame.K_SPACE and (rocket_state == "ready") and (not game_over_flag):
                rocket_sound.play()
                rocket_x = player_x
                rocket_y = 480.0
                rocket_state = "fire"

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                player_vx = 0.0

    # Update (only if not game over)
    if not game_over_flag:
        # Player movement + boundaries
        player_x += player_vx * dt
        player_x = clamp(player_x, 0.0, WIDTH - 64.0)

        # Rocket movement
        if rocket_state == "fire":
            rocket_y -= ROCKET_SPEED * dt
            if rocket_y <= -15:
                rocket_state = "ready"

        # Enemy movement + collisions
        for e in enemies:
            # Check game over condition
            if e["y"] > 450:
                game_over_flag = True
                # push all enemies off-screen like your original
                for ee in enemies:
                    ee["y"] = 2000.0
                break

            e["x"] += e["vx"] * dt

            # Bounce off edges and drop
            if e["x"] <= 0.0:
                e["x"] = 0.0
                e["vx"] = abs(e["vx"])
                e["y"] += ENEMY_DROP
            elif e["x"] >= WIDTH - 64.0:
                e["x"] = WIDTH - 64.0
                e["vx"] = -abs(e["vx"])
                e["y"] += ENEMY_DROP

            # Collision (use rocket tip-ish coordinates; keep simple)
            if rocket_state == "fire" and is_collision(e["x"], e["y"], rocket_x, rocket_y):
                explosion_sound.play()
                score_value += 1

                # Reset rocket
                rocket_state = "ready"
                rocket_y = 480.0

                # Respawn enemy
                e["x"] = float(random.randint(0, WIDTH - 65))
                e["y"] = float(random.randint(50, 150))

    # Draw
    screen.fill(WHITE)
    screen.blit(background, (0, 0))

    # Enemies
    for e in enemies:
        draw_enemy(e["x"], e["y"])

    # Rocket
    if rocket_state == "fire":
        draw_rocket(rocket_x, rocket_y)

    # Player + UI
    draw_player(player_x, player_y)
    draw_score()

    if game_over_flag:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
