import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Load car image
car_width, car_height = 50, 100
player_car = pygame.Surface((car_width, car_height))
player_car.fill(RED)

# Initial car position
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 20
car_speed = 5

# Obstacles
obstacle_width, obstacle_height = 50, 100
obstacle_speed = 5
obstacles = []
max_obstacles = 1  # Start with one obstacle
lanes = WIDTH // obstacle_width  # Number of possible lanes

# Score
score = 0
font = pygame.font.Font(None, 36)

def create_obstacle():
    occupied_lanes = {obs.x // obstacle_width for obs in obstacles}  # Track occupied lanes
    available_lanes = [i for i in range(lanes) if i not in occupied_lanes]
    
    # Ensure at least 2-3 free lanes for movement
    if len(available_lanes) < 3:
        return None
    
    x_lane = random.choice(available_lanes)
    x_pos = x_lane * obstacle_width
    return pygame.Rect(x_pos, -obstacle_height, obstacle_width, obstacle_height)

def move_obstacles():
    global obstacles, score, obstacle_speed, max_obstacles, car_speed
    passed_obstacles = []
    for obs in obstacles:
        obs.y += obstacle_speed
        if obs.y >= HEIGHT:  # If obstacle passes the screen
            passed_obstacles.append(obs)
    
    # Remove passed obstacles and increase score
    for obs in passed_obstacles:
        obstacles.remove(obs)
        score += 1
    
    # Increase speed every 10 points
    if score % 10 == 0:
        obstacle_speed += 0.05
        car_speed += 0.05  # Increase car speed as well
    
    # Increase number of obstacles every 10 points
    if score % 10 == 0 and max_obstacles < lanes - 3:
        max_obstacles += 10

def check_collision():
    player_rect = pygame.Rect(car_x, car_y, car_width, car_height)
    for obs in obstacles:
        if player_rect.colliderect(obs):
            return True
    return False

def show_game_over():
    screen.fill(BLACK)
    game_over_text = font.render("Game Over!", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - 50, HEIGHT // 2 - 20))
    screen.blit(score_text, (WIDTH // 2 - 50, HEIGHT // 2 + 20))
    pygame.display.update()
    pygame.time.delay(2000)

def slow_down_before_game_over():
    global obstacle_speed
    for i in range(5, 0, -1):  # Gradually decrease speed
        obstacle_speed = i
        pygame.time.delay(300)
        pygame.display.update()
    show_game_over()

running = True
clock = pygame.time.Clock()
spawn_timer = 0

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car_x > 0:
        car_x -= car_speed
    if keys[pygame.K_RIGHT] and car_x < WIDTH - car_width:
        car_x += car_speed
    
    # Spawn obstacles
    spawn_timer += 1
    if spawn_timer > 50 and len(obstacles) < max_obstacles:
        new_obstacle = create_obstacle()
        if new_obstacle:
            obstacles.append(new_obstacle)
        spawn_timer = 0
    
    move_obstacles()
    
    # Draw player car
    screen.blit(player_car, (car_x, car_y))
    
    # Draw obstacles
    for obs in obstacles:
        pygame.draw.rect(screen, BLACK, obs)
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    if check_collision():
        slow_down_before_game_over()
        running = False
    
    pygame.display.update()
    clock.tick(30)

pygame.quit()
