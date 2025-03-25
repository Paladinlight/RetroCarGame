import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COUNTER FLOW")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (88, 255, 88)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (100, 100, 100)

# Fonts
font = pygame.font.Font("assets/fonts/MegamaxJones-elRm.ttf", 20)
med_font = pygame.font.Font("assets/fonts/SuperPixel-m2L8j.ttf", 25)
large_font = pygame.font.Font("assets/fonts/SuperPixel-m2L8j.ttf", 30)

# Difficulty levels with stages
difficulties = {
    "Easy": [(1, 2, False), (2, 4, False), (5, 5, True)],
    "Medium": [(1, 2, False), (2, 4, False), (5, 5, True)],
    "Hard": [(1, 2, False), (2, 4, False), (5, 5, True)]
}

difficulty = "Medium"
current_level = 0
player_speed = 3
enemy_speed = 5

# UI State
game_active = False
difficulty_selection = False
game_over = False

# Car dimensions
car_width, car_height = 50, 60
player_car = pygame.Rect(WIDTH // 2 - car_width // 2, HEIGHT - 120, car_width, car_height)

# Enemy car settings
enemy_width, enemy_height = 50, 60
enemy_cars = []
follower_enemy = None  # Enemy that follows the player

# Score
score = 0

def set_difficulty(level):
    global difficulty, player_speed, enemy_speed, enemy_cars, game_active, difficulty_selection, current_level, follower_enemy
    difficulty = level
    current_level = 0
    player_speed = 3 + (list(difficulties.keys()).index(difficulty))
    enemy_speed = player_speed + 2
    follower_enemy = None
    setup_level()
    game_active = True
    difficulty_selection = False

def setup_level():
    global enemy_cars, follower_enemy
    num_min, num_max, has_follower = difficulties[difficulty][current_level]
    enemy_cars = [
        pygame.Rect(random.randint(50, WIDTH - 50), random.randint(-300, -50), enemy_width, enemy_height)
        for _ in range(random.randint(num_min, num_max))
    ]
    if has_follower:
        follower_enemy = pygame.Rect(WIDTH // 2, -100, enemy_width, enemy_height)
    else:
        follower_enemy = None

def advance_level():
    global current_level, game_active, game_over
    if current_level < len(difficulties[difficulty]) - 1:
        current_level += 1
        setup_level()
    else:
        game_over = True
        game_active = False

def trigger_game_over():
    global game_active, game_over
    game_active = False
    game_over = True

def draw_text(text, font, color, x, y):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, text_rect)

def draw_button(text, x, y, w, h, color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    draw_text(text, font, BLACK, x + w // 2, y + h // 2)
    if button_rect.collidepoint(mouse) and click[0] == 1 and action:
        pygame.time.delay(150)
        action()

def show_difficulty_selection():
    global difficulty_selection
    difficulty_selection = True

def reset_game():
    global game_active, difficulty_selection, game_over, score
    game_active = False
    difficulty_selection = False
    game_over = False
    score = 0

running = True
clock = pygame.time.Clock()
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_active and not difficulty_selection and not game_over:
        draw_text("CounterFlow", large_font, BLACK, WIDTH // 2, 200)
        draw_text("Survive", med_font, RED, WIDTH // 2, 250)
        draw_button("Start", WIDTH // 2 - 75, HEIGHT // 2, 150, 50, RED, show_difficulty_selection)
    elif difficulty_selection:
        draw_text("Select Difficulty", large_font, BLACK, WIDTH // 2, 180)
        draw_button("Easy", WIDTH // 2 - 75, 250, 150, 50, GREEN, lambda: set_difficulty("Easy"))
        draw_button("Medium", WIDTH // 2 - 75, 320, 150, 50, YELLOW, lambda: set_difficulty("Medium"))
        draw_button("Hard", WIDTH // 2 - 75, 390, 150, 50, ORANGE, lambda: set_difficulty("Hard"))
    elif game_active:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_car.x > 0:
            player_car.x -= player_speed
        if keys[pygame.K_RIGHT] and player_car.x < WIDTH - car_width:
            player_car.x += player_speed

        for enemy in enemy_cars:
            enemy.y += enemy_speed
            if enemy.y > HEIGHT:
                enemy.y = -100
                enemy.x = random.randint(50, WIDTH - 50)
                score += 1
                if score % 10 == 0:
                    advance_level()

        if follower_enemy:
            follower_enemy.y += enemy_speed
            if follower_enemy.x < player_car.x:
                follower_enemy.x += 2
            elif follower_enemy.x > player_car.x:
                follower_enemy.x -= 2

        for enemy in enemy_cars:
            if player_car.colliderect(enemy):
                trigger_game_over()
        if follower_enemy and player_car.colliderect(follower_enemy):
            trigger_game_over()

        pygame.draw.rect(screen, BLUE, player_car)
        for enemy in enemy_cars:
            pygame.draw.rect(screen, RED, enemy)
        if follower_enemy:
            pygame.draw.rect(screen, ORANGE, follower_enemy)

        draw_text(f"Score: {score} Level: {current_level + 1}", font, BLACK, 70, 20)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
