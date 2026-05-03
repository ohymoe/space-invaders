import pygame
import random
import math
from pygame import mixer

# initializing pygame
#helllo
pygame.init()

# creating screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width,
                                  screen_height))

# caption and icon
pygame.display.set_caption("Welcome to Space\
Invaders Game by:- styles")


# Score
score_val = 0
scoreX = 5
scoreY = 5
font = pygame.font.Font('freesansbold.ttf', 20)

# Game Over
game_over_font = pygame.font.Font('freesansbold.ttf', 64)


def show_score(x, y):
    score = font.render("Points: " + str(score_val),
                        True, (255,255,255))
    screen.blit(score, (x , y ))

def game_over():
    game_over_text = game_over_font.render("GAME OVER",
                                           True, (255,255,255))
    screen.blit(game_over_text, (190, 250))

# i stole this code
def scale_keep_aspect(image, target_width):
    # Calculate the ratio
    ratio = target_width / image.get_width()
    target_height = int(image.get_height() * ratio)
    return pygame.transform.smoothscale(image, (target_width, target_height))

# Background Sound
#mixer.music.load('data/background.wav')
#mixer.music.play(-1)


# player
tardis = pygame.image.load('data/tardis.png')
playerImage = scale_keep_aspect(tardis, 60)

player_X = 370
player_Y = 470
player_Xchange = 0


# Invader
invaderImage = []
invader_X = []
invader_Y = []
invader_Xchange = []
invader_Ychange = []
no_of_invaders = 8

for num in range(no_of_invaders):
    invaderImage.append(pygame.image.load('data/dalek.png'))
    invader_X.append(random.randint(64, 737))
    invader_Y.append(random.randint(30, 180))
    invader_Xchange.append(0.2)
    invader_Ychange.append(25)

# Bullet
# rest - bullet is not moving
# fire - bullet is moving
laser = pygame.image.load('data/laser.png')
bulletImage = scale_keep_aspect(laser, 65)
bullet_X = 0
bullet_Y = 500
bullet_Xchange = 0
bullet_Ychange = 3
bullet_state = "rest"

#enemy shooting 
#current_shooting system 
current_chooter = None 


# enemy bullets 
enemy_bullets = []
enemy_bullet_speed = 2


# Collision Concept
def isCollision(x1, x2, y1, y2):
    distance = math.sqrt((math.pow(x1 - x2,2)) +
                         (math.pow(y1 - y2,2)))
    if distance <= 50:
        return True
    else:
        return False

def player(x, y):
    screen.blit(playerImage, (x - 16, y + 10))

def invader(x, y, i):
    screen.blit(invaderImage[i], (x, y))

def bullet(x, y):
    global bullet_state
    screen.blit(bulletImage, (x, y))
    bullet_state = "fire"

# game loop
running = True
while running:

    # RGB
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Controlling the player movement
        # from the arrow keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_Xchange = -1.7
            if event.key == pygame.K_RIGHT:
                player_Xchange = 1.7
            if event.key == pygame.K_SPACE:
              
                # Fixing the change of direction of bullet
                if bullet_state is "rest":
                    bullet_X = player_X - 16 + playerImage.get_width() // 2 - bulletImage.get_width() // 2
                    bullet_Y = player_Y + 10 - bulletImage.get_height()
                    bullet(bullet_X, bullet_Y)
                    # bullet_sound = mixer.Sound('data/bullet.wav')
                    # bullet_sound.play()
        if event.type == pygame.KEYUP:
            player_Xchange = 0 

    # adding the change in the player position
    player_X += player_Xchange
    for i in range(no_of_invaders):
        invader_X[i] += invader_Xchange[i]

        if random.randint(1, 200) == 1:  # 1-in-200 chance per frame
            enemy_bullets.append([invader_X[i] + 16, invader_Y[i] + 20])


    # bullet movement
    if bullet_Y <= 0:
        bullet_Y = 600
        bullet_state = "rest"
    if bullet_state is "fire":
        bullet(bullet_X, bullet_Y)
        bullet_Y -= bullet_Ychange

        # Move and draw enemy bullets
    for b in enemy_bullets:
        b[1] += enemy_bullet_speed
        screen.blit(bulletImage, (b[0], b[1]))

        # Check collision between enemy bullets and player
    for b in enemy_bullets:
        if abs(b[0] - player_X) < 30 and abs(b[1] - player_Y) < 30:
            print(f"[DEBUG] Player HIT by enemy bullet at ({b[0]}, {b[1]})")
            enemy_bullets.remove(b)

            # Player hit — end game or reduce health
            # game_over()

        # Remove off-screen enemy bullets
    enemy_bullets = [b for b in enemy_bullets if b[1] < 600]


    # movement of the invader
    for i in range(no_of_invaders):
        
        if invader_Y[i] >= 450:
            if abs(player_X-invader_X[i]) < 80:
                for j in range(no_of_invaders):
                    invader_Y[j] = 2000
                    # explosion_sound = mixer.Sound('data/explosion.wav')
                    # explosion_sound.play()
                # game_over()
                break

        if invader_X[i] >= 735 or invader_X[i] <= 0:
            invader_Xchange[i] *= -1
            invader_Y[i] += invader_Ychange[i]
        # Collision
        collision = isCollision(bullet_X, invader_X[i],
                                bullet_Y, invader_Y[i])
        if collision:
            score_val += 1
            bullet_Y = 600
            bullet_state = "rest"
            # keep the invader down so it doesn’t respawn
            invader_X[i] = -200
            invader_Y[i] = -200
            invader_Xchange[i] = 0

        if invader_Y[i] >= 0:
            invader(invader_X[i], invader_Y[i], i)


    # restricting the spaceship so that
    # it doesn't go out of screen
    if player_X <= 16:
        player_X = 16
    elif player_X >= 750:
        player_X = 750


    player(player_X, player_Y)
    show_score(scoreX, scoreY)
    pygame.display.update()