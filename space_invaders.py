
import pygame as pg
import random
import math
import os, sys
import socket
import threading

pg.init()

# --- GLOBALS ---- ┌( ಠ_ಠ)┘
PORT = 5050
sock = None
incoming_messages = []
role = None
mode = None

# creating screen
screen_width = 800
screen_height = 600
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("tardis invaders")

player_speed = 1
bullet_speed = 3
enemy_bullet_speed = 1

left_held = False 
right_held = False

# ----ASSET HELPER FUNCTIONS----
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)

def scale_keep_aspect(image, target_width):
    # Calculate the ratio
    ratio = target_width / image.get_width()
    target_height = int(image.get_height() * ratio)
    return pg.transform.smoothscale(image, (target_width, target_height))

# ---ASSETS----

start_bg = pg.image.load(resource_path("data/start_screen.png"))
bg = pg.image.load(resource_path("data/background.png"))
game_bg = scale_keep_aspect(bg, 910).convert()

tardis = pg.image.load(resource_path('data/tardis.png'))
laser = pg.image.load(resource_path('data/laser.png'))
playerImage = scale_keep_aspect(tardis, 60)
bulletImage = scale_keep_aspect(laser, 65)

# ---- FONTS ---- 
scoreX = 5
scoreY = 5

font = pg.font.Font("data\Press_Start_2P\PressStart2P-Regular.ttf", 20)
game_over_font = pg.font.Font("data\Press_Start_2P\PressStart2P-Regular.ttf", 50)
game_won_font = pg.font.Font("data\Press_Start_2P\PressStart2P-Regular.ttf", 50)
title_font = pg.font.Font("data\Press_Start_2P\PressStart2P-Regular.ttf", 40)
subhead_font = pg.font.Font("data\Press_Start_2P\PressStart2P-Regular.ttf", 16)

# ---- NETWORKING -----

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

    send_message("JOINED") #tell host i joined!11

    thread = threading.Thread(target=listen_for_messages, args=(sock,), daemon=True)
    thread.start()

def send_message(msg: str):
    global sock    
    if sock:
        try:
            sock.sendall((msg + "\n").encode("utf-8"))
        except OSError:
            pass

# --- LOBBIES ----
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_server():
    import subprocess
    try:
        subprocess.Popen([sys.executable, "server.py"])
    except:
        pass

def host_lobby():
    player_joined = False
    local_ip = get_local_ip()
    clock = pg.time.Clock()

    while True:
        screen.fill((0, 0, 0))
        screen.blit(font.render(f"Your IP: {local_ip}", True, (255,255,255)), (20,180))

        while incoming_messages:
            msg = incoming_messages.pop(0)
            if msg.startswith("ROLE:"):
                _, role = msg.split(":")
            elif msg == "JOINED":
                player_joined = True

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and player_joined:
                if event.key == pg.K_RETURN:
                    send_message("START")
                    return
                
        if player_joined:
            info1 = font.render("Players ready!", True, (255,255,255))
            info2 = font.render("ENTER to start", True, (255,255,255))
            screen.blit(info2, (20, 260))
        else:
            info1 = font.render("Waiting for other player...", True, (255,255,255))

        screen.blit(info1, (20, 220))
        pg.display.update()            
        clock.tick(30)

def join_lobby():
    global role
    clock = pg.time.Clock()
    while True:
        while incoming_messages:
            msg = incoming_messages.pop(0)
            if msg.startswith("ROLE:"):
                _, role = msg.split(":")
            elif msg == "START":
                return True
    
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        title = title_font.render("JOIN LOBBY", True, (255,255,255))
        info1 = font.render("Waiting for host to start... chop chop", True, (255,255,255))

        screen.blit(title, (20, 150))
        screen.blit(info1, (20, 260))
        pg.display.update()
        clock.tick(30)


left_held = False
right_held = False


# Invader
invaderImage = []
invader_X = []
invader_Y = []
invader_Xchange = []
invader_Ychange = []
invader_alive = []
no_of_invaders = 8

for num in range(no_of_invaders):
    invaderImage.append(pg.image.load(resource_path('data/dalek.png')))
    invader_X.append(0)
    invader_Y.append(0)
    invader_Xchange.append(0)
    invader_Ychange.append(0)
    invader_alive.append(True)

# bullets
bullet_speed = 3
# enemy bullets 
enemy_bullet_speed = 1
local_bullets = []
remote_bullets = []
enemy_bullets = []

# shooting system 
shooting = False 
shoot_timer = 0
shoot_duration = 1500
shoot_cooldown = 3000
current_shooter = None





def init_globals():
    global player_X, player_Y, player_Xchange, player2_X, player2_Y, player2_Xchange
    global player_lives, score_val, running
    global invader_X, invader_Y, invader_alive
    global local_bullets, remote_bullets, enemy_bullets
    global role, shooting, shoot_timer, current_shooter 
    global left_held, right_held

    # global sock
    # if sock:
    #     try:
    #         sock.close()
    #     except:
    #         pass
    # sock = None

    # player positions
    player_X = 370
    player_Y = 470
    player_Xchange = 0

    # remote player position
    player2_X = 370
    player2_Y = 470
    player2_Xchange = 0

    left_held = False
    right_held = False

    player_lives = 3
    score_val = 0
    running = True 

    role = None
    incoming_messages.clear()
    local_bullets.clear()
    remote_bullets.clear()
    enemy_bullets.clear()

    for i in range(no_of_invaders):
        invader_X[i] = random.randint(64, 737)
        invader_Y[i] = random.randint(30, 180)
        invader_Xchange[i] = 0.2
        invader_Ychange[i] = 25
        invader_alive[i] = True

    shooting = False
    shoot_timer = 0
    current_shooter = None

def remote_input():
    global player2_Xchange, running, player_lives, score_val, player_speed, role

    while incoming_messages:
        msg = incoming_messages.pop(0)
        if msg.startswith("ROLE:"):
            _, role = msg.split(":")
        if msg == "MOVE LEFT":
            player2_Xchange = -player_speed
        elif msg == "MOVE RIGHT":
            player2_Xchange = player_speed
        elif msg == "MOVE STOP":
            player2_Xchange = 0
        elif msg == "SHOOT":
            remote_bullets.append([
                player2_X - 16 + playerImage.get_width()//2 - bulletImage.get_width()//2,
                player2_Y - bulletImage.get_height()
            ])
        elif msg.startswith("ENEMY"):
            _, idx, x, y, alive = msg.split()
            idx = int(idx)
            invader_X[idx] = int(x)
            invader_Y[idx] = int(y)
            invader_alive[idx] = bool(int(alive))
        elif msg.startswith("EBULLET"):
            _, x, y = msg.split()
            enemy_bullets.append([float(x), float(y)])
        elif msg.startswith("LIVES"):
            _, val = msg.split()
            player_lives = int(val)
        
        elif msg == "GAME OVER":
            game_over()
            running = False
        elif msg == "GAME WON":
            game_won()
            running = False
        elif msg.startswith("SCORE"):
            _, val = msg.split()
            score_val = int(val)
        


def show_score(x, y):
    score = font.render("Points: " + str(score_val),
                        True, (255,255,255))
    screen.blit(score, (x , y ))
    lives = font.render("Lives: " + str(player_lives),
                        True, (255,255,255))
    screen.blit(lives, (x, y + 30))

def game_over():
    screen.fill((0, 0, 0))

    game_over_text = game_over_font.render("GAME OVER", True, (255,255,255))
    screen.blit(game_over_text, (180, 200))

    score_text = font.render("Final Score: " + str(score_val), True, (255,255,255))
    screen.blit(score_text, (250, 300))

    prompt = font.render("Press ENTER to return to menu", True, (255,255,255))
    screen.blit(prompt, (125, 450))

    pg.display.update()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return False
def game_won():
    screen.fill((0, 0, 0))

    game_won_text = game_won_font.render("congrats!", True, (255,255,255))
    subhead = subhead_font.render("you've commited a mass murder.", True, (255,255,255))
    screen.blit(game_won_text, (170, 200))
    screen.blit(subhead, (160, 300))

    prompt = font.render("Press ENTER to return to menu", True, (255,255,255))
    screen.blit(prompt, (125, 450))

    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return False



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
    
    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return None
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    return "solo"
                if event.key == pg.K_h:
                    return "host"
                if event.key == pg.K_j:
                    return "join"

def events():
    global running, left_held, right_held, player_Xchange

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                left_held = True
            if event.key == pg.K_RIGHT:
                right_held = True
            if event.key == pg.K_SPACE:
                local_bullets.append([
                    player_X - 16 + playerImage.get_width()//2 - bulletImage.get_width()//2,
                    player_Y - bulletImage.get_height()
                ])
                send_message("SHOOT")

        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                left_held = False
            if event.key == pg.K_RIGHT:
                right_held = False
# local 
    if left_held and not right_held:
        player_Xchange = -player_speed
        send_message("MOVE LEFT")
    elif right_held and not left_held:
        player_Xchange = player_speed
        send_message("MOVE RIGHT")
    else:
        player_Xchange = 0
        send_message("MOVE STOP")

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

def move_remote_player():
    global player2_X
    player2_X += player2_Xchange
    player2_X = max(16, min(750, player2_X))
    
def update_bullet(bullets):
    for b in bullets[:]:
        b[1] -= bullet_speed
        screen.blit(bulletImage, (b[0], b[1]))
        if b[1] < 0:
            bullets.remove(b)


def update_enemy_bullets():
    global player_lives, running, enemy_bullets
    for b in enemy_bullets:
        b[1] += enemy_bullet_speed
        enemy_bullet(b[0], b[1])
    
        player1_hit = isCollision(b[0], player_X, b[1], player_Y)
        player2_hit = isCollision(b[0], player2_X, b[1], player2_Y)
        
        if player1_hit or player2_hit:
            player_lives -= 1
            enemy_bullets.remove(b)
        if role == "P1":
            send_message(f"LIVES {player_lives}")

    enemy_bullets = [b for b in enemy_bullets if b[1] < 600]
def check_hit_invader(bullets, inv_i):
    global score_val

    for b in bullets[:]:
        if isCollision(b[0], invader_X[inv_i], b[1], invader_Y[inv_i]):
            score_val += 1

            if role == "P1":
                send_message(f"SCORE {score_val}")

            bullets.remove(b)

            invader_X[inv_i] = -200 # offscreen
            invader_Y[inv_i] = -200
            invader_Xchange[inv_i] = 0
            invader_alive[inv_i] = False
            return True   
    return False

def update_invaders():
    global score_val, bullet_Y, current_shooter, shooting, shoot_timer, enemy_bullets

    # movement of the invader
    for i in range(no_of_invaders):
        invader_X[i] += invader_Xchange[i]
        if invader_Y[i] >= 450:
            if abs(player_X-invader_X[i]) < 80:
                for j in range(no_of_invaders):
                    invader_Y[j] = 2000
                game_over()
                break
        
        if invader_X[i] >= 735 or invader_X[i] <= 0:
            invader_Xchange[i] *= -1
            invader_Y[i] += invader_Ychange[i]

        if check_hit_invader(local_bullets, i):
            continue
        if check_hit_invader(remote_bullets, i):
            continue
        if invader_Y[i] >= 0:
            invader(invader_X[i], invader_Y[i], i)
        
        if shooting and i == current_shooter:
            if random.randint(1,300) == 1:
                bx = invader_X[i] + invaderImage[i].get_width() // 2 - bulletImage.get_width() // 2
                by = invader_Y[i] + invaderImage[i].get_height()

                enemy_bullets.append([bx, by])                
                print(f"enemy {i} fired")
                if role == "P1":
                    send_message(f"EBULLET {bx} {by}")
    
def render_invaders():
    for i in range(no_of_invaders):
        if invader_alive[i] and invader_Y[i] >= 0:
            invader(invader_X[i], invader_Y[i], i)

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
    if role == "P2":
        screen.blit(playerImage, (player2_X - 16, player2_Y + 10))
    show_score(scoreX, scoreY)

def main():    
    global running
    running = True
    won = False
    remote_bullets.clear()

    while running:
        screen.blit(game_bg, (0, 0))

        events()
        move_player()
        update_bullet(local_bullets)
        update_invaders()
        update_enemy_bullets()
        update_shooting()
        draw()

        pg.display.update()

        if player_lives <= 0:
            running = False 
        
        if all(not alive for alive in invader_alive):
            running = False
            won = True

    return won
        




        
            
def join_input():

    ip_str = ""
    clock = pg.time.Clock()

    while True:

        screen.fill((0, 0, 0))
        title = title_font.render("JOIN GAME", True, (255,255,255))
        prompt = font.render("Enter host IP on host's screen: ", True, (255,255,255))
        ip_render = font.render(ip_str + "_", True, (0,255,0))

        screen.blit(title, (20, 150))
        screen.blit(prompt, (20, 220))
        screen.blit(ip_render, (20, 260))

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return None
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return ip_str.strip()
                elif event.key == pg.K_BACKSPACE:
                    ip_str = ip_str[:-1]
                else:
                    if len(event.unicode) == 1 and (event.unicode.isdigit() or event.unicode == '.' or event.unicode == ':'):
                        ip_str += event.unicode

        clock.tick(30)



def main_multiplayer():
    global running
    running = True
    while running:
        screen.blit(game_bg, (0, 0))

        events()               # local input
        remote_input()         # remote input
        move_player()          # move local
        move_remote_player()   # move remote
        update_bullet(local_bullets)
        update_bullet(remote_bullets)

        if role == "P1":
            update_invaders()     
            update_enemy_bullets()
            update_shooting()

        #sync enemy positions 
            for i in range(no_of_invaders):
                send_message(f"ENEMY {i} {int(invader_X[i])} {int(invader_Y[i])} {int(invader_alive[i])}")

            if player_lives <= 0:
                running = False
                send_message("GAME OVER")
                game_over()

            if all(not alive for alive in invader_alive):
                send_message("GAME WON")
                running = False
                game_won()
    
        else:
            render_invaders()
            update_enemy_bullets()

        draw()
        pg.display.update()




if __name__ == "__main__":
    server_started = False

    while True:
        mode = start_menu()
        init_globals()
        if mode == "solo":
            role = "P1"
            won = main()
            if player_lives <= 0:
                game_over()
            elif won:
                game_won()

        if mode == "host":
            role = "P1"
            if not server_started:
                run_server() # start server in background
                server_started = True
                import time
                time.sleep(0.4)
            start_client("127.0.0.1")
            host_lobby()
            main_multiplayer()
            
        if mode == "join":
            role = "P2"
            # ip = join_input()
            # if ip:
            #     start_client(ip)
            start_client("127.0.0.1") # for testing
            join_lobby()
            main_multiplayer()