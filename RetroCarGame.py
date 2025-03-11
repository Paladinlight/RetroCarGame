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

# Difficulty levels
difficulties = {"Easy": 3, "Medium": 5, "Hard": 7}
difficulty = "Medium"
player_speed = difficulties[difficulty]
enemy_speed = difficulties[difficulty] + 2

# UI State
game_active = False
difficulty_selection = False
game_over = False

# Car dimensions
car_width, car_height = 50, 60
player_car = pygame.Rect(WIDTH // 2 - car_width // 2, HEIGHT - 120, car_width, car_height)

# Enemy car settings
enemy_width, enemy_height = 50, 60
enemy_cars = []  # List to store multiple enemy cars

# Score
score = 0

# Button function
def draw_button(text, x, y, w, h, base_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, w, h)

    # Adjust color on hover
    if button_rect.collidepoint(mouse):
        hover_color = (max(base_color[0] - 40, 0), max(base_color[1] - 40, 0), max(base_color[2] - 40, 0))
        color = hover_color if not click[0] else DARK_GRAY
    else:
        color = base_color

    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(text_surf, text_rect)

    if button_rect.collidepoint(mouse) and click[0] == 1 and action:
        pygame.time.delay(150)  # Prevent multiple rapid clicks
        action()

# Change difficulty
def set_difficulty(level):
    global difficulty, player_speed, enemy_speed, enemy_cars, game_active, difficulty_selection
    difficulty = level
    player_speed = difficulties[difficulty]
    enemy_speed = difficulties[difficulty] + 2

    num_enemies = {"Easy": 2, "Medium": 3, "Hard": 5}
    enemy_cars = [
        pygame.Rect(random.randint(50, WIDTH - 50), random.randint(-300, -50), enemy_width, enemy_height)
        for _ in range(num_enemies[difficulty])
    ]
    game_active = True
    difficulty_selection = False

# Start game
def show_difficulty_selection():
    global difficulty_selection
    difficulty_selection = True

def reset_game():
    global game_active, difficulty_selection, game_over, score
    game_active = False
    difficulty_selection = False
    game_over = False
    score = 0

def trigger_game_over():
    global game_active, game_over
    game_active = False
    game_over = True

# Running the game
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_active and not difficulty_selection and not game_over:
        # Display menu
        title_text1 = large_font.render("CounterFlow", True, BLACK)
        screen.blit(title_text1, (WIDTH // 2 - title_text1.get_width() // 2, 200))
        
        title_text2 = med_font.render("Survive", True, RED)
        screen.blit(title_text2, (WIDTH // 2 - title_text2.get_width() // 2, 250))
        
        draw_button("Start", WIDTH // 2.15 - 75, HEIGHT // 2, 180, 60, RED, show_difficulty_selection)
    elif difficulty_selection:
        difficulty_text = large_font.render("Select Difficulty", True, BLACK)
        screen.blit(difficulty_text, (WIDTH // 2 - difficulty_text.get_width() // 2, 180))
        
        draw_button("Easy", WIDTH // 2 - 75, 250, 150, 50, GREEN, lambda: set_difficulty("Easy"))
        draw_button("Medium", WIDTH // 2 - 75, 320, 150, 50, YELLOW, lambda: set_difficulty("Medium"))
        draw_button("Hard", WIDTH // 2 - 75, 390, 150, 50, ORANGE, lambda: set_difficulty("Hard"))
    elif game_over:
        game_over_text = large_font.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
        
        score_text = large_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 3 + 50))
        
        draw_button("Back to Menu", WIDTH // 2.15 - 75, HEIGHT // 2, 180, 60, GRAY, reset_game)
    else:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_car.x > 0:
            player_car.x -= player_speed
        if keys[pygame.K_RIGHT] and player_car.x < WIDTH - car_width:
            player_car.x += player_speed

        # Move enemy cars
        for enemy in enemy_cars:
            enemy.y += enemy_speed
            if enemy.y > HEIGHT:
                enemy.y = -100
                enemy.x = random.randint(50, WIDTH - 50)
                score += 1  # Increase score when enemy resets

        # Check for collision
        for enemy in enemy_cars:
            if player_car.colliderect(enemy):
                trigger_game_over()

        # Draw player car
        pygame.draw.rect(screen, BLUE, player_car)

        # Draw enemy cars
        for enemy in enemy_cars:
            pygame.draw.rect(screen, RED, enemy)

        # Display score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
