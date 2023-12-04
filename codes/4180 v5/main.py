# Import necessary libraries
import pygame
import random
import time
from dataclasses import dataclass
from gpiozero import DistanceSensor
from threading import Thread,Lock
import os 

# open necessary files
keyfile = open('keycodes.txt','w')
distancefile = open('distanceFlag.txt','w')

# Initialize Pygame
pygame.init()

# Load and scale the background image
bg_image = pygame.image.load('background2.png')
bg_image = pygame.transform.scale(bg_image, (bg_image.get_width() * 3, bg_image.get_height() * 3))

# Create the game screen
screen = pygame.display.set_mode((bg_image.get_width(), bg_image.get_height()))

# Load and scale the enemy image
enemy_image = pygame.image.load("mole.png")
enemy_image = pygame.transform.scale(enemy_image, (enemy_image.get_width() // 2, enemy_image.get_height() // 2))

# Initialize the score and font
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

# Set the initial position for displaying the score
textX = 10
textY = 10

# game duration time
game_start_time = 0
game_duration = 30

# Initialize the list to store enemy objects
enemies = []

# Set the number of columns and rows for the enemy grid
NUM_COL = 3
NUM_ROW = 3

# Set the lifespan of enemies in milliseconds
ENEMY_LIFE_SPAN = 5 * 1000

# Define the Enemy data class using dataclasses module
@dataclass
class Enemy:
    x: int
    y: int
    life: int = ENEMY_LIFE_SPAN

# Set the radius, color, and events for enemy generation and aging
ENEMY_RADIUS = min(enemy_image.get_width(), enemy_image.get_height()) // 2.5
ENEMY_COLOR = (255, 0, 0)
GENERATE_ENEMY = pygame.USEREVENT + 1
AGE_ENEMY = pygame.USEREVENT + 2
global APPEAR_INTERVAL
global AGE_INTERVAL
APPEAR_INTERVAL = 1000
AGE_INTERVAL = 500

# Define possible initial positions for enemies
possible_enemy_pos = [(150 + 320 * x, 70 + 150 * y) for y in range(NUM_ROW) for x in range(NUM_COL)]
'''
possible_enemy_pos = [(150, 70), (470, 70), (790, 70), 
                      (150, 220), (470, 220), (790, 220), 
                      (150, 370), (470, 370), (790, 370)]
'''

# Function to check if an enemy already exists at a given position
def check_exist(pos):
    for enemy in enemies:
        if pos == (enemy.x, enemy.y):
            return True
    return False

# Function to generate a new position for the next enemy
def generate_next_enemy_pos():
    new_pos = ()
    while True:
        grid_index = random.randint(0, NUM_ROW * NUM_COL - 1) # 0~8
        new_pos = possible_enemy_pos[grid_index]
        if not check_exist(new_pos):
            break
    return new_pos

# Function to draw enemies on the screen
def draw_enemies():
    for enemy in enemies:
        screen.blit(enemy_image, (enemy.x, enemy.y))

# Function to display the score on the screen
def show_score(x, y):
    global score_value
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

# Function to display the left_time on the screen
def show_time(total_time, current_time, x, y):
    time = font.render("Time: " + str(int(total_time-current_time)), True, (255, 255, 255))
    screen.blit(time, (x, y))

# Function to check if a click position collides with a specific enemy
def check_enemy_collision(clickX, clickY, enemyX, enemyY):
    if clickX == enemyX and clickY == enemyY:
        return True
    return False

# Function to check collision with all enemies and update the score
def check_enemies_collision(click_pos, enemies):
    for enemy in enemies:
        if check_enemy_collision(click_pos[0], click_pos[1], enemy.x, enemy.y):
            global score_value
            score_value += 1
            enemies.remove(enemy)

# Function to decrease the lifespan of enemies
def age_enemies():
    for enemy in enemies:
        enemy.life = enemy.life - 1000

# Function to remove dead enemies (lifespan reached zero)
def remove_died_enemies():
    for enemy in enemies:
        if enemy.life == 0:
            enemies.remove(enemy)
            
# Function to reset game page            
def reset_game():
    global score_value, game_start_time, enemies, play_status
    score_value = 0
    game_start_time = time.time()
    enemies = []
    play_status = True
    pygame.time.set_timer(GENERATE_ENEMY, APPEAR_INTERVAL)
    pygame.time.set_timer(AGE_ENEMY, AGE_INTERVAL)
    
    
# Global variables to store the latest key code and distance flag
latest_keycode = None
latest_distance_flag = None
data_lock = Lock()
def read_last_line(filename):
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            if lines:
                return lines[-1].strip()
    except IOError:
        return None
    return None

def update_latest_data():
    global latest_keycode, latest_distance_flag
    while True:
        with data_lock:
            latest_keycode = read_last_line("keycodes.txt")
            latest_distance_flag = read_last_line("distanceFlag.txt")
        time.sleep(0.1)  # Adjust as needed
        
# Start the thread for reading keycodes and distance flags
Thread(target=update_latest_data, daemon=True).start()

# Main game loop
# difficult initial setting
select_difficulty = True
difficult_level = [(150, 70), (470, 220), (790, 370)] # easy, medium, hard
for level in difficult_level:
    enemies.append(Enemy(level[0], level[1]))
difficult = (0,0)

# game initialization
play_status = True
running = True
selected_hole = (0,0)
total = -1
key_num = 0
# game loop
while running:
    with data_lock:
        keycode = latest_keycode
        distance_flag = latest_distance_flag
    # convert real key code 
    if keycode == "08":
        key_num = 0
    elif keycode == "04":
        key_num = 1
    elif keycode == "00":
        key_num = 2
    elif keycode == "09":
        key_num = 3
    elif keycode == "05":
        key_num = 4
    elif keycode == "01":
        key_num = 5
    elif keycode == "10":
        key_num = 6
    elif keycode == "06":
        key_num = 7
    elif keycode == "02":
        key_num = 8
    # change keycode to coordinate
    selected_hole  = possible_enemy_pos[key_num] # change click position to game coordinate
    difficult = possible_enemy_pos[key_num]
    
    # hit action
    if distance_flag == "1":
        if select_difficulty:
            if difficult in difficult_level:
                if difficult == (150, 70):
                    APPEAR_INTERVAL = 2 * 1000
                    AGE_INTERVAL = 1 * 1000
                elif difficult == (470, 220):
                        APPEAR_INTERVAL = 1 * 1000
                        AGE_INTERVAL = 500
                elif difficult == (790, 370):
                        APPEAR_INTERVAL = 500
                        AGE_INTERVAL = 250
                reset_game()
                select_difficulty = False      
        
        if not select_difficulty and play_status:
            check_enemies_collision(selected_hole, enemies)       
                    
    # collect event        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False        
        if (not select_difficulty) and play_status:
            if event.type == AGE_ENEMY:
                age_enemies()
                remove_died_enemies()
            if event.type == GENERATE_ENEMY:
                if len(enemies) < NUM_COL * NUM_ROW:
                    new_pos = generate_next_enemy_pos()
                    enemies.append(Enemy(new_pos[0], new_pos[1]))
                    total +=1
    
    # game over
    if not select_difficulty and time.time() - game_start_time > game_duration:
        play_status = False    

    # Check if the game is over and update the display accordingly
    if not play_status:
        # Set background to pure black
        screen.fill((0, 0, 0))

        # Display "Game Over!" in the center of the screen in red
        if score_value == total:
            game_over_text = font.render("Game Over!", True, (0, 255, 0))
        else:
            game_over_text = font.render("Game Over!", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(bg_image.get_width() // 2, bg_image.get_height() // 2))
        screen.blit(game_over_text, text_rect)

        # Display the final score
        final_score_text = font.render(f"Your Score: {score_value}/{total}", True, (255, 255, 255))
        score_rect = final_score_text.get_rect(center=(bg_image.get_width() // 2, text_rect.bottom + 20))
        screen.blit(final_score_text, score_rect)
        
        if difficult in [(150, 70), (470, 220), (790, 370)]:
            if difficult == (150, 70):
                level_text = font.render("Your level: Easy", True, (255, 255, 255))
            elif difficult == (470, 220):
                level_text = font.render("Your level: Medium", True, (255, 255, 255))
            elif difficult == (790, 370):
                level_text = font.render("Your level: Hard", True, (255, 255, 255))
            level_rect = level_text.get_rect(center=(bg_image.get_width() // 2, text_rect.bottom + 60))
            screen.blit(level_text, level_rect)
    
    else:
        screen.blit(bg_image, (0, 0))
        draw_enemies()
        
        # Game is still running, update other elements
        if not select_difficulty: 
            show_score(textX, textY)
            show_time(game_duration, time.time() - game_start_time, textX, textY + 40)
        
        else:
            Easy_text = font.render("Easy", True, (255, 255, 255))
            Easy_rect = Easy_text.get_rect(center=(350, 300))
            screen.blit(Easy_text, Easy_rect)
            Medium_text = font.render("Medium", True, (255, 255, 255))
            Medium_rect = Easy_text.get_rect(center=(650, 450))
            screen.blit(Medium_text, Medium_rect)
            Hard_text = font.render("Hard", True, (255, 255, 255))
            Hard_rect = Hard_text.get_rect(center=(990, 600))
            screen.blit(Hard_text, Hard_rect)
            
    pygame.display.update()
    
keyfile = open('keycodes.txt','w').close()
distancefile = open('distanceFlag.txt','w').close()
