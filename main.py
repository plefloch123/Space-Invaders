import random
import math
import time

import pygame
from pygame import mixer

# initialize the pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800,600))

# Background
background = pygame.image.load("background.jpg")

# Background Sound
mixer.music.load("game_bakcground.mp3")
mixer.music.play(-1)

# Title and Icon
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load("ufo.png")
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load("player.png")
playerX = 370
playerY = 525
playerX_change = 0

# Score
score_value = 0
font = pygame.font.Font("freesansbold.ttf", 32)

textX = 10
textY = 10

#Game Over Text
over_font = pygame.font.Font("freesansbold.ttf", 64)

textX = 10
textY = 10

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 12

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load("alien.png"))
    enemyX.append(random.randint(0,735))
    enemyY.append(random.randint(50,150))
    enemyX_change.append(0.5)
    enemyY_change.append(40)

# Rocket

# Ready - You can't see the bullet on the screen
# Fire - You can see the rocket moving
rocketImg = pygame.image.load("bullet.png")
rocketX = 0
rocketY = 480
rocketX_change = 0
rocketY_change = 3
rocket_state = "ready"

def game_over(x,y):
   over_text = over_font.render("GAME OVER : " + str(score_value), True, (255, 255, 255))
   screen.blit(over_text, (200, 250))

def show_score(x,y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (textX, textY))

def player(x,y):
    screen.blit(playerImg,(x,y))

def enemy(x,y, i):
    screen.blit(enemyImg[i],(x,y))

def fire_rocket(x,y):
    global rocket_state
    rocket_state = "fire"
    screen.blit(rocketImg,(x + 16,y + 10))# Appear on center of spaceship

def isCollision(enemyX,enemyY,rocketX,rocketY):
    distance = math.sqrt((math.pow(enemyX-rocketX,2)) + (math.pow(enemyY-rocketY,2)))
    if distance < 27:
        return True

# Game Loop
running = True

while running:

    screen.fill((255, 255, 255))

    # Background image
    screen.blit(background,(0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -1.0
            if event.key == pygame.K_RIGHT:
                playerX_change = 1.0
            if event.key == pygame.K_SPACE:
                if rocket_state is "ready":
                    rocket_sound = mixer.Sound("laser.wav")
                    rocket_sound.play()
                    rocketX = playerX
                    fire_rocket(rocketX,rocketY)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    # Player movement with boundaries
    playerX += playerX_change
    if playerX <= 0:
        playerX_change = 0
    elif playerX >= 736: #Because size of spaceship is 64 pixel so 800-64 = 736
        playerX_change = 0

    # Enemy movement
    for i in range(num_of_enemies):

        # Game Over
        if enemyY[i] > 450:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over(textX,textY)
            break

        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0 or enemyX[i] >= 736:
            enemyX_change[i] = -enemyX_change[i]
            enemyY[i] += enemyY_change[i]

        # Collision
        collision = isCollision(enemyX[i], enemyY[i], rocketX, rocketY)
        if collision:
            collision_sound = mixer.Sound("explosion.wav")
            collision_sound.play()
            rocketY = 480
            rocket_state= "ready"
            score_value += 1
            enemyX[i] = random.randint(0, 735)
            enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)

    # Rocket movement
    if rocketY <= -15:
        rocketY = 480
        rocket_state = "ready"

    # Define when rocket is ready
    if rocket_state is "fire":
        fire_rocket(rocketX,rocketY)
        rocketY -= rocketY_change

    player(playerX,playerY)
    show_score(textX,textY)
    pygame.display.update()