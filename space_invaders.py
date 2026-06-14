import pygame
import random
import math
from pygame import mixer

import socket
import threading

PORT = 5050
sock = None
incoming_messages = []
role = None


# listeneer thread 
def listen_for_messages(s):
    global incoming_messages
    try:
        reader = s.makefile("r", encoding="utf-8")
        for line in reader:
            msg = line.rstrip("\n")
            incoming_messages.append(msg)
    except OSError:
        pass

def start_client(host_ip):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host_ip, PORT))

    thread = threading.Thread(target=listen_for_messages, args=(sock,), daemon=True)
    thread.start()

def send_message(msg: str):
    global sock
    if sock is None:
        return
    try:
        sock.sendall((msg + "\n").encode("utf-8"))
    except OSError:
        pass


# initializing pygame
#helllo
pygame.init()

import os, sys

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


# creating screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width,
                                  screen_height))

# caption and icon
pygame.display.set_caption("space invaders....")

player_lives = 3  

# Score
score_val = 0
scoreX = 5
scoreY = 5
font = pygame.font.Font('freesansbold.ttf', 20)


# Game Over
game_over_font = pygame.font.Font('freesansbold.ttf', 64)
game_won_font = pygame.font.Font('freesansbold.ttf', 64)
title_font = pygame.font.Font('freesansbold.ttf', 40)
#subhead_font = pygame.font.Font('freesansbold.ttf', 16)

def show_score(x, y):
    score = font.render("Points: " + str(score_val),
                        True, (255,255,255))
    screen.blit(score, (x , y ))
    lives = font.render("Lives: " + str(player_lives),
                        True, (255,255,255))
    screen.blit(lives, (x, y + 30))

def game_over():
    screen.fill((0, 0, 0))
    game_over_text = game_over_font.render("GAME OVER",
                                           True, (255,255,255))
    screen.blit(game_over_text, (190, 250))

    score_text = font.render("Final Score: " + str(score_val),
                             True, (255,255,255))
    screen.blit(score_text, (320, 350))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

def game_won():
    screen.fill((0, 0, 0))

    game_won_text = game_won_font.render("congrats!", True, (255,255,255))
    subhead = font.render("you've commited a mass murder.", True, (255,255,255))
    screen.blit(game_won_text, (240, 200))
    screen.blit(subhead, ( 235, 300))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False



# AI written
def scale_keep_aspect(image, target_width):
    # Calculate the ratio
    ratio = target_width / image.get_width()
    target_height = int(image.get_height() * ratio)
    return pygame.transform.smoothscale(image, (target_width, target_height))

# Background Sound
#mixer.music.load('data/background.wav')
#mixer.music.play(-1)

# bg images
start_bg = pygame.image.load(resource_path("data/start_screen.png"))
bg = pygame.image.load(resource_path("data/background.png"))
game_bg = scale_keep_aspect(bg, 910).convert()

# player
tardis = pygame.image.load(resource_path('data/tardis.png'))
playerImage = scale_keep_aspect(tardis, 60)

class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.speed = 1
        self.xchange = 0
        self.lives = 3
        self.image = image

    def move(self):
        self.x += self.xchange
        self.x = max(16, min(750, self.x))

    def draw(self, screen):
        screen.blit(self.image, (self.x - 16, self.y + 10))


player_X = 370
player_Y = 470
player_Xchange = 0
player_speed = 1

# Invader
invaderImage = []
invader_X = []
invader_Y = []
invader_Xchange = []
invader_Ychange = []
no_of_invaders = 8
invader_alive = [True] * no_of_invaders

for num in range(no_of_invaders):
    invaderImage.append(pygame.image.load(resource_path('data/dalek.png')))
    invader_X.append(random.randint(64, 737))
    invader_Y.append(random.randint(30, 180))
    invader_Xchange.append(0.2)
    invader_Ychange.append(25)

# Bullet
# rest - bullet is not moving
# fire - bullet is moving
laser = pygame.image.load(resource_path('data/laser.png'))
bulletImage = scale_keep_aspect(laser, 65)
bullet_X = 0
bullet_Y = 500
bullet_Xchange = 0
bullet_Ychange = 3
bullet_state = "rest"

#enemy shooting 

# shooting system 
shooting = False 
shoot_timer = 0
shoot_duration = 1500
shoot_cooldown = 3000
current_shooter = None


# enemy bullets 
enemy_bullets = []
enemy_bullet_speed = 1


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

def enemy_bullet(x, y):
    screen.blit(bulletImage, (x, y))


def start_menu():
    screen.blit(start_bg, (0, 0))

    title = title_font.render("SPACE INVADERS", True, (255,255,255))
    subtitle1 = font.render("SPACE = Solo", True, (255,255,255))
    subtitle2 = font.render("H = Host Multiplayer", True, (255,255,255))
    subtitle3 = font.render("J = Join Multiplayer", True, (255,255,255))

    screen.blit(title, (20, 200))
    screen.blit(subtitle1, (20, 260))
    screen.blit(subtitle2, (20, 300))
    screen.blit(subtitle3, (20, 340))
    
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "solo"
                if event.key == pygame.K_h:
                    return "host"
                if event.key == pygame.K_j:
                    return "join"


def events():
    global running, player_Xchange, bullet_state, bullet_X, bullet_Y

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Controlling the player movement
        # from the arrow keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_Xchange = -player_speed
            if event.key == pygame.K_RIGHT:
                player_Xchange = player_speed
            if event.key == pygame.K_SPACE:
              
                # Fixing the change of direction of bullet
                if bullet_state == "rest":
                    bullet_X = player_X - 16 + playerImage.get_width() // 2 - bulletImage.get_width() // 2
                    bullet_Y = player_Y + 10 - bulletImage.get_height()
                    bullet(bullet_X, bullet_Y)
                    # bullet_sound = mixer.Sound('data/bullet.wav')
                    # bullet_sound.play()
        if event.type == pygame.KEYUP:
            player_Xchange = 0 

def move_player():
    global player_X
        # adding the change in the player position
    player_X += player_Xchange

    # restricting the spaceship so that
    # it doesn't go out of screen
    if player_X <= 16:
        player_X = 16
    elif player_X >= 750:
        player_X = 750

def update_bullet():
    global bullet_Y, bullet_state

    for i in range(no_of_invaders):
        invader_X[i] += invader_Xchange[i]
        
    # bullet movement
    if bullet_Y <= 0:
        bullet_Y = 600
        bullet_state = "rest"

    if bullet_state == "fire":
        bullet(bullet_X, bullet_Y)
        bullet_Y -= bullet_Ychange

def update_enemy_bullets():
    global player_lives, running, enemy_bullets
    for b in enemy_bullets:
        b[1] += enemy_bullet_speed
        enemy_bullet(b[0], b[1])
    
        player_hit = isCollision(b[0], player_X, b[1], player_Y)
        
        if player_hit:
            player_lives -= 1
            enemy_bullets.remove(b)
            print(f"player hit. Lives remaining: {player_lives}")

    enemy_bullets = [b for b in enemy_bullets if b[1] < 600]

def update_invaders():
    global score_val, bullet_Y, bullet_state, current_shooter, shooting, shoot_timer, enemy_bullets

    # movement of the invader
    for i in range(no_of_invaders):
        
        if invader_Y[i] >= 450:
            if abs(player_X-invader_X[i]) < 80:
                for j in range(no_of_invaders):
                    invader_Y[j] = 2000
                game_over()
                break
        
        if invader_X[i] >= 735 or invader_X[i] <= 0:
            invader_Xchange[i] *= -1
            invader_Y[i] += invader_Ychange[i]

    # Collision with player bullet
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
            invader_alive[i] = False

        if invader_Y[i] >= 0:
            invader(invader_X[i], invader_Y[i], i)
        
        if shooting and i == current_shooter:
            if random.randint(1,300) == 1:
                enemy_bullets.append([invader_X[i] + invaderImage[i].get_width() // 2 - bulletImage.get_width() //2, invader_Y[i] + invaderImage[i].get_height()])
                print(f"enemy {i} fired")

def update_shooting():
    global shooting, shoot_timer, current_shooter
    shoot_timer += 1

    # start shooting
    if not shooting: 
        if shoot_timer > shoot_cooldown:
            shooting = True
            shoot_timer = 0

            enemies_alive = []
            for i in range(no_of_invaders):
                if invader_alive[i]:
                    enemies_alive.append(i)
            if enemies_alive:
                current_shooter = random.choice(enemies_alive)
            else:
                current_shooter = None
                
            print("Enemies start shooting")

    # stop shooting 
    if shooting and shoot_timer > shoot_duration: 
        shooting = False
        shoot_timer = 0
        current_shooter = None
        print("Enemies stop shooting")

def draw():
    player(player_X, player_Y)
    show_score(scoreX, scoreY)




def main():    
    global running
    running = True
    won = False
    while running:
        screen.blit(game_bg, (0, 0))

        events()
        move_player()
        update_bullet()
        update_invaders()
        update_enemy_bullets()
        update_shooting()
        draw()

        pygame.display.update()

        if player_lives <= 0:
            running = False 
        
        if all(not alive for alive in invader_alive):
            running = False
            won = True
    return won
        



if __name__ == "__main__":
    mode = start_menu()

    if mode == "solo":
        won = main()
        if player_lives <= 0:
            game_over()
        elif won:
            game_won()
        pygame.quit()
    if mode == "host":
        # runs solo for now, will add multiplayer later
        role = "P1"
        start_client("127.0.0.1")
        won = main()
        if player_lives <= 0:
            game_over()
        elif won:
            game_won()
        pygame.quit()

    if mode == "join":
        role = "P2"
        ip = input("Enter host IP: ")
        start_client(ip)
        # runs solo for now, will add multiplayer later
        won = main()
        if player_lives <= 0:
            game_over()
        elif won:
            game_won()
        pygame.quit()        