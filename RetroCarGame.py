import os
import warnings
import pygame
import random
import sys
import uuid
import json

# Suppress warnings and pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.filterwarnings("ignore", category=UserWarning, message="libpng warning: iCCP")

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 720, 600
ROAD_X = 98
ROAD_WIDTH = 350
TREE_ZONE_WIDTH = 50
ROAD_SCROLL_SPEED = 5
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'SCORE_TEXT': (255, 255, 255),
    'ROAD': (50, 50, 50)
}

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COUNTER FLOW")

# Game state flags
game_active = False
difficulty_selection = False
game_over = False
show_welcome = False
welcome_timer = 0
show_leaderboard = False

# Road animation variables
road_y = 0
CAR_WIDTH, CAR_HEIGHT = 40, 60
PLAYER_CAR_WIDTH, PLAYER_CAR_HEIGHT = 64, 64
SAVE_FILE = "players.json"

def generate_uid():
    return str(uuid.uuid4())

def save_new_player(username="Player One"):
    uid = generate_uid()
    player_data = {"uid": uid, "username": username, "score": 0}
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[uid] = player_data
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    return player_data

def load_players():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, "r") as f:
        return json.load(f)

def select_existing_player():
    players = load_players()
    if not players:
        return None
    # For now, just pick the first player (no input UI)
    first_uid = next(iter(players))
    return players[first_uid]

def select_existing_player_menu(screen, font):
    players = load_players()
    if not players:
        return None
    player_list = list(players.values())
    selected = 0
    selecting = True
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(player_list)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(player_list)
                elif event.key == pygame.K_RETURN:
                    return player_list[selected]

        screen.fill((30, 30, 30))
        title = font.render("Select Player", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        for i, p in enumerate(player_list):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            txt = font.render(f"{p['username']} (High Score: {p['score']})", True, color)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 150 + i*40))
        pygame.display.flip()

def save_player_score(uid, score):
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        if uid in data and score > data[uid]["score"]:
            data[uid]["score"] = score
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)

def get_player_rank(uid):
    players = load_players()
    scores = sorted([(p['uid'], p['score']) for p in players.values()], key=lambda x: x[1], reverse=True)
    for idx, (pid, _) in enumerate(scores):
        if pid == uid:
            return idx + 1
    return None

def create_default_car(color):
    """Create a simple car surface if assets are missing"""
    car = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(car, color, (10, 0, CAR_WIDTH-20, CAR_HEIGHT-20), border_radius=5)
    pygame.draw.rect(car, (200, 200, 200), (15, 5, CAR_WIDTH-30, CAR_HEIGHT-30), border_radius=3)
    return car

def create_default_tree():
    """Create a simple tree surface if assets are missing"""
    tree = pygame.Surface((40, 80), pygame.SRCALPHA)
    pygame.draw.rect(tree, (139, 69, 19), (15, 40, 10, 40))  # trunk
    pygame.draw.circle(tree, (0, 100, 0), (20, 30), 20)  # leaves
    return tree

def load_assets():
    assets = {
        'background': None,
        'road': None,
        'player_car': create_default_car((0, 0, 255)),  # Blue player car
        'enemy_cars': {
            'down_left': None,  # Left lane (faster)
            'down_right': None  # Right lane (slower)
        },
        'tree': create_default_tree(),
        'fonts': {
            'main': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 50),
            'score': pygame.font.Font(None, 36),
            'tiny': pygame.font.Font(None, 18)  # Add this line
        }
    }
    
    try:
        # Try loading actual assets
        assets['background'] = pygame.image.load("assets/CARS/bg.png").convert()
        assets['background'] = pygame.transform.scale(assets['background'], (WIDTH, HEIGHT))
        assets['desertbg'] = pygame.image.load("assets/CARS/desertbg.png").convert()
        assets['desertbg'] = pygame.transform.scale(assets['desertbg'], (WIDTH, HEIGHT))
        assets['dirtbg'] = pygame.image.load("assets/CARS/dirtbg.png").convert()
        assets['dirtbg'] = pygame.transform.scale(assets['dirtbg'], (WIDTH, HEIGHT))
        assets['road'] = pygame.image.load("assets/CARS/road.png").convert_alpha()
        assets['road'] = pygame.transform.scale(assets['road'], (ROAD_WIDTH, HEIGHT))
        tree_img = pygame.image.load("assets/CARS/tree.png").convert_alpha()
        tree_width, tree_height = tree_img.get_width(), tree_img.get_height()
        scale_factor = 2  # Change this to make it bigger or smaller
        assets['tree'] = pygame.transform.scale(tree_img, (tree_width * scale_factor, tree_height * scale_factor))
        assets['desert_rock'] = pygame.transform.scale(
            pygame.image.load("assets/CARS/desertRock.png").convert_alpha(),
            (69, 67)  # Use the actual size or scale as needed
        )
        assets['burned_tree'] = pygame.transform.scale(
            pygame.image.load("assets/CARS/burned_tree.png").convert_alpha(),
            (48, 48)  # Use the actual size or scale as needed
        )
        
        # Load actual car images if available
        player_img = pygame.image.load("assets/CARS/maincarLOw.png").convert_alpha()
        assets['player_car'] = pygame.transform.scale(player_img, (PLAYER_CAR_WIDTH, PLAYER_CAR_HEIGHT))
        
        # Load enemy cars - different images for left and right lanes
        enemy_down_left = pygame.image.load("assets/CARS/car-enemy2.png").convert_alpha()
        assets['enemy_cars']['down_left'] = pygame.transform.scale(enemy_down_left, (CAR_WIDTH, CAR_HEIGHT))
        
        enemy_down_right = pygame.image.load("assets/CARS/car-enemy.png").convert_alpha()
        assets['enemy_cars']['down_right'] = pygame.transform.scale(enemy_down_right, (CAR_WIDTH, CAR_HEIGHT))
        
        # Try loading fonts
        assets['fonts']['main'] = pygame.font.Font("assets/fonts/PixelifySans-Bold.ttf", 36)
        assets['fonts']['large'] = pygame.font.Font("assets/fonts/MegamaxJones-elRm.ttf", 50)
        assets['fonts']['score'] = pygame.font.Font("assets/fonts/PixelifySans-Bold.ttf", 36)
        assets['fonts']['tiny'] = pygame.font.Font("assets/fonts/PixelifySans-regular.ttf", 20)
    except Exception as e:
        print(f"Asset loading error: {e}, using default assets")
        # Create different colored cars for left and right lanes
        assets['enemy_cars']['down_left'] = create_default_car((255, 0, 0))  # Red for left lane
        assets['enemy_cars']['down_right'] = create_default_car((255, 100, 0))  # Orange for right lane
    
    return assets

class Tree:
    def __init__(self, side, image_key='tree'):
        self.side = side  # 'left' or 'right'
        self.image_key = image_key
        self.image = assets[self.image_key]
        self.rect = self.image.get_rect()
        self.reset()
        
    def set_image(self, image_key):
        self.image_key = image_key
        self.image = assets[self.image_key]
        old_pos = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = old_pos

    def reset(self):
        self.rect.y = random.randint(-HEIGHT, -100)
        if self.side == 'left':
            self.rect.x = random.randint(10, ROAD_X - TREE_ZONE_WIDTH)
        else:
            self.rect.x = random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 50)

    def update(self):
        self.rect.y += ROAD_SCROLL_SPEED
        if self.rect.top > HEIGHT:
            self.reset()

class GameData:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.current_level = 0
        self.player_speed = 5
        self.enemy_speed_left = 6
        self.enemy_speed_right = 2
        self.base_min_cars = 2
        self.base_max_cars = 3
        self.score = 0
        self.enemy_cars = []
        self.trees = []
        self.just_leveled_up = False

        self.player_rect = pygame.Rect(
            ROAD_X + (ROAD_WIDTH // 2) - (CAR_WIDTH // 2),
            HEIGHT - 120,
            CAR_WIDTH,
            CAR_HEIGHT
        )

        # Improved tree placement
        tree_positions = []
        min_distance = 60  # Minimum distance between trees
        tree_width = assets['tree'].get_width()
        tree_height = assets['tree'].get_height()

        def valid_tree_pos(x, y, side):
            # Avoid road area
            if side == 'left' and (x + tree_width > ROAD_X - 5):
                return False
            if side == 'right' and (x < ROAD_X + ROAD_WIDTH + 5):
                return False
            # Avoid overlap with other trees
            for tx, ty in tree_positions:
                if abs(x - tx) < min_distance and abs(y - ty) < min_distance:
                    return False
            return True

        # Place left trees
        for _ in range(4):
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                x = random.randint(10, ROAD_X - tree_width - 10)
                y = random.randint(-HEIGHT, HEIGHT - tree_height)
                if valid_tree_pos(x, y, 'left'):
                    tree_positions.append((x, y))
                    t = Tree('left')
                    t.rect.x = x
                    t.rect.y = y
                    self.trees.append(t)
                    placed = True
                attempts += 1

        # Place right trees
        for _ in range(4):
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                x = random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - tree_width - 10)
                y = random.randint(-HEIGHT, HEIGHT - tree_height)
                if valid_tree_pos(x, y, 'right'):
                    tree_positions.append((x, y))
                    t = Tree('right')
                    t.rect.x = x
                    t.rect.y = y
                    self.trees.append(t)
                    placed = True
                attempts += 1

        self.setup_level()

    def setup_level(self):
        # Cars increase every 5 levels
        extra_cars = self.current_level // 5
        min_cars = self.base_min_cars + extra_cars
        max_cars = self.base_max_cars + extra_cars

        # Speed increases by 10% per level
        self.enemy_speed_left = 6 * (2.2 ** self.current_level)
        self.enemy_speed_right = 2 * (2.2 ** self.current_level)

        self.enemy_cars = []
        left_lane = ROAD_X
        right_lane = ROAD_X + ROAD_WIDTH - CAR_WIDTH
        mid_point = ROAD_X + (ROAD_WIDTH // 2) - (CAR_WIDTH // 2)

        for _ in range(random.randint(min_cars, max_cars)):
            if random.random() < 0.5:
                x_pos = random.randint(left_lane, mid_point - 10)
                speed = self.enemy_speed_left
                sprite = assets['enemy_cars']['down_left']
            else:
                x_pos = random.randint(mid_point + 10, right_lane)
                speed = self.enemy_speed_right
                sprite = assets['enemy_cars']['down_right']

            enemy_rect = pygame.Rect(
                x_pos,
                random.randint(-300, -50),
                CAR_WIDTH,
                CAR_HEIGHT
            )
            self.enemy_cars.append((enemy_rect, sprite, speed))

def simple_collision(rect1, rect2):
    """Simpler collision detection using rects only"""
    return rect1.colliderect(rect2)

def handle_difficulty(level):
    global game_active, difficulty_selection
    game_data.difficulty = level
    game_data.reset()
    game_active = True
    difficulty_selection = False

def draw_text(text, font, color, x, y):
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, text_surf.get_rect(center=(x, y)))

def create_button(text, x, y, w, h, color):
    return {
        'rect': pygame.Rect(x, y, w, h),
        'color': color,
        'text': text
    }

def draw_manual_panel(screen, font):
    panel_width = 250
    panel_height = 180
    panel_x = WIDTH - panel_width - 20
    panel_y = 400
    panel_color = (30, 30, 30, 200)  # RGBA for transparency

    # Create a semi-transparent surface
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surface.fill(panel_color)

    # Manual text (smaller font)
    manual_text = [
        "HOW TO PLAY:",
        "Arrow <- ->",
        "keyboar A D: Move",
        "Avoid enemy cars",
        "Collect power-ups",
        "Level up at milestones"
    ]
    # Use the tiny font from assets
    tiny_font = assets['fonts']['tiny']
    for i, line in enumerate(manual_text):
        text = tiny_font.render(line, True, (255, 255, 255))
        panel_surface.blit(text, (12, 10 + i * 24))  # Adjust line spacing for tiny font

    screen.blit(panel_surface, (panel_x, panel_y))

def draw_top_right_info(screen, font, username, score, high_score, rank):
    text1 = font.render(username, True, (255, 255, 255))
    text2 = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    text3 = font.render(f"Rank: {rank}", True, (255, 255, 255))
    screen.blit(text1, (screen.get_width() - text1.get_width() - 10, 10))
    screen.blit(text2, (screen.get_width() - text2.get_width() - 10, 40))
    screen.blit(text3, (screen.get_width() - text3.get_width() - 10, 70))

def get_username_input(screen, font):
    username = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 12 and event.unicode.isprintable():
                    username += event.unicode

        screen.fill((30, 30, 30))
        prompt = font.render("Enter Username:", True, (255, 255, 255))
        usertxt = font.render(username, True, (255, 255, 0))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 60))
        screen.blit(usertxt, (WIDTH//2 - usertxt.get_width()//2, HEIGHT//2))
        pygame.display.flip()
    return username.strip()

def draw_leaderboard(screen, font):
    players = load_players()
    sorted_players = sorted(players.values(), key=lambda p: p['score'], reverse=True)
    screen.fill((30, 30, 30))
    title = font.render("LEADERBOARD", True, (255, 215, 0))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
    for i, p in enumerate(sorted_players[:10]):
        entry = font.render(f"{i+1}. {p['username']} - {p['score']}", True, (255, 255, 255))
        screen.blit(entry, (WIDTH//2 - entry.get_width()//2, 120 + i*40))
    info = font.render("Press ESC to return", True, (200, 200, 200))
    screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 60))
    pygame.display.flip()

def fade_transition(screen, from_bg, to_bg, duration=800):
    clock = pygame.time.Clock()
    steps = 30
    for alpha in range(0, 256, int(255/steps)):
        temp = to_bg.copy()
        temp.set_alpha(alpha)
        screen.blit(from_bg, (0, 0))
        screen.blit(temp, (0, 0))
        pygame.display.flip()
        clock.tick(steps / (duration / 1000))

# Initialize game data
assets = load_assets()
game_data = GameData()
BG_SEQUENCE = [assets['background'], assets['desertbg'], assets['dirtbg']]

# Player system: load or create
if os.path.exists(SAVE_FILE):
    player = select_existing_player()
    if player is None:
        player = save_new_player()
else:
    player = save_new_player()

# Main game loop
running = True
clock = pygame.time.Clock()
manual_shown = False  # Add this flag
paused = False

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and game_active:
                paused = not paused
            if paused and event.key == pygame.K_s:
                paused = False  # "Skip" resumes the game

    # --- PAUSE CHECK: Do this BEFORE any game logic or drawing ---
    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        pause_text = assets['fonts']['large'].render("PAUSED", True, COLORS['YELLOW'])
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 40))
        skip_text = assets['fonts']['main'].render("Press S to skip", True, COLORS['WHITE'])
        screen.blit(skip_text, (WIDTH//2 - skip_text.get_width()//2, HEIGHT//2 + 30))
        pygame.display.flip()
        clock.tick(10)
        continue  # Skip the rest of the loop, so nothing moves/updates

    # --- All your game logic and drawing below here ---
    # Update road animation, draw background, trees, road, game states, etc.

    # Update road animation
    road_y = (road_y + ROAD_SCROLL_SPEED) % HEIGHT

    # Choose background based on level
    bg_index = game_data.current_level % len(BG_SEQUENCE)
    bg = BG_SEQUENCE[bg_index]
    screen.blit(bg, (0, 0))

    # Set tree image depending on background
    if bg_index == 0:
        tree_key = 'tree'
    elif bg_index == 1:
        tree_key = 'desert_rock'
    else:
        tree_key = 'burned_tree'

    for tree in game_data.trees:
        tree.set_image(tree_key)
        tree.update()
        screen.blit(tree.image, tree.rect)

    # Draw road
    if assets['road']:
        screen.blit(assets['road'], (ROAD_X, road_y))
        screen.blit(assets['road'], (ROAD_X, road_y - HEIGHT))
    else:
        pygame.draw.rect(screen, COLORS['ROAD'], (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
        # Draw road markings
        for i in range(-1, HEIGHT//50 + 1):
            y_pos = (i * 50 + road_y) % HEIGHT
            pygame.draw.rect(screen, COLORS['YELLOW'], (ROAD_X + ROAD_WIDTH//2 - 5, y_pos, 10, 30))

    # Game states
    # Main menu state
    if not game_active and not difficulty_selection and not game_over and not show_leaderboard:
        draw_text("COUNTER FLOW", assets['fonts']['large'], COLORS['WHITE'], WIDTH//2, 150)
        draw_text("Avoid the oncoming traffic!", assets['fonts']['main'], COLORS['RED'], WIDTH//2, 200)

        new_btn = create_button("NEW GAME", WIDTH//2-100, 300, 200, 50, COLORS['GREEN'])
        load_btn = create_button("LOAD GAME", WIDTH//2-100, 370, 200, 50, COLORS['YELLOW'])
        leaderboard_btn = create_button("LEADERBOARD", WIDTH//2-125, 440, 250, 50, COLORS['ORANGE'])

        pygame.draw.rect(screen, new_btn['color'], new_btn['rect'], border_radius=10)
        draw_text(new_btn['text'], assets['fonts']['main'], COLORS['BLACK'], new_btn['rect'].centerx, new_btn['rect'].centery)
        pygame.draw.rect(screen, load_btn['color'], load_btn['rect'], border_radius=10)
        draw_text(load_btn['text'], assets['fonts']['main'], COLORS['BLACK'], load_btn['rect'].centerx, load_btn['rect'].centery)
        pygame.draw.rect(screen, leaderboard_btn['color'], leaderboard_btn['rect'], border_radius=10)
        draw_text(leaderboard_btn['text'], assets['fonts']['main'], COLORS['BLACK'], leaderboard_btn['rect'].centerx, leaderboard_btn['rect'].centery)

        if mouse_click:
            if new_btn['rect'].collidepoint(mouse_pos):
                username = get_username_input(screen, assets['fonts']['main'])
                player = save_new_player(username)
                game_data.reset()
                show_welcome = True
                welcome_timer = pygame.time.get_ticks()
                game_active = False
                difficulty_selection = False
            elif load_btn['rect'].collidepoint(mouse_pos):
                loaded = select_existing_player_menu(screen, assets['fonts']['main'])
                if loaded:
                    player = loaded
                    game_data.reset()
                    show_welcome = True
                    welcome_timer = pygame.time.get_ticks()
                    game_active = False
                    difficulty_selection = False
            elif leaderboard_btn['rect'].collidepoint(mouse_pos):
                show_leaderboard = True

    elif difficulty_selection:
        # Difficulty selection
        draw_text("SELECT DIFFICULTY", assets['fonts']['large'], COLORS['WHITE'], WIDTH//2, 150)
        
        buttons = [
            create_button("EASY", WIDTH//2-100, 250, 200, 50, COLORS['GREEN']),
            create_button("MEDIUM", WIDTH//2-100, 320, 200, 50, COLORS['YELLOW']),
            create_button("HARD", WIDTH//2-100, 390, 200, 50, COLORS['RED'])
        ]
        
        for i, btn in enumerate(buttons):
            pygame.draw.rect(screen, btn['color'], btn['rect'], border_radius=10)
            draw_text(btn['text'], assets['fonts']['main'], COLORS['BLACK'], btn['rect'].centerx, btn['rect'].centery)
            
            if mouse_click and btn['rect'].collidepoint(mouse_pos):
                handle_difficulty(btn['text'].upper())
    
    elif game_over:
        # Game over screen
        draw_text("GAME OVER", assets['fonts']['large'], COLORS['RED'], WIDTH//2, 150)
        draw_text(f"SCORE: {game_data.score}", assets['fonts']['main'], COLORS['WHITE'], WIDTH//2, 220)
        
        # Create buttons
        play_again_btn = create_button("PLAY AGAIN", WIDTH//2-100, 300, 200, 50, COLORS['GREEN'])
        quit_btn = create_button("QUIT", WIDTH//2-100, 370, 200, 50, COLORS['RED'])
        
        # Draw buttons
        pygame.draw.rect(screen, play_again_btn['color'], play_again_btn['rect'], border_radius=10)
        draw_text(play_again_btn['text'], assets['fonts']['main'], COLORS['BLACK'], 
                 play_again_btn['rect'].centerx, play_again_btn['rect'].centery)
        
        pygame.draw.rect(screen, quit_btn['color'], quit_btn['rect'], border_radius=10)
        draw_text(quit_btn['text'], assets['fonts']['main'], COLORS['BLACK'], 
                 quit_btn['rect'].centerx, quit_btn['rect'].centery)
        
        # Handle button clicks
        if mouse_click:
            if play_again_btn['rect'].collidepoint(mouse_pos):
                game_data.reset()
                road_y = 0
                game_over = False
                game_active = True
            elif quit_btn['rect'].collidepoint(mouse_pos):
                running = False

        save_player_score(player['uid'], game_data.score)
    
    elif game_active:
        # Gameplay controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game_data.player_rect.x = max(ROAD_X, game_data.player_rect.x - game_data.player_speed)
        if keys[pygame.K_RIGHT]:
            game_data.player_rect.x = min(ROAD_X + ROAD_WIDTH - CAR_WIDTH, 
                                        game_data.player_rect.x + game_data.player_speed)

        # Update enemies with different speeds for each lane
        for i, (enemy_rect, sprite, speed) in enumerate(game_data.enemy_cars):
            enemy_rect.y += speed  # Move downward at assigned speed
            
            # Reset if gone past bottom of screen
            if enemy_rect.top > HEIGHT:
                enemy_rect.y = random.randint(-300, -50)
                # Keep same lane by checking x position
                if enemy_rect.x < ROAD_X + (ROAD_WIDTH // 2):
                    # Left lane - faster
                    enemy_rect.x = random.randint(ROAD_X, ROAD_X + (ROAD_WIDTH // 2) - 10)
                    speed = game_data.enemy_speed_left
                    sprite = assets['enemy_cars']['down_left']  # Maintain correct sprite
                else:
                    # Right lane - slower
                    enemy_rect.x = random.randint(ROAD_X + (ROAD_WIDTH // 2) + 10, ROAD_X + ROAD_WIDTH - CAR_WIDTH)
                    speed = game_data.enemy_speed_right
                    sprite = assets['enemy_cars']['down_right']  # Maintain correct sprite
                game_data.enemy_cars[i] = (enemy_rect, sprite, speed)
                game_data.score += 1

            # Check collision
            if simple_collision(game_data.player_rect, enemy_rect):
                # Visual feedback for collision
                screen.fill(COLORS['RED'])
                pygame.display.flip()
                pygame.time.delay(200)
                game_active = False
                game_over = True

        # Improved infinite level progression
        if game_data.score > 0 and game_data.score % 20 == 0 and not game_data.just_leveled_up:
            game_data.just_leveled_up = True
            game_data.current_level += 1
            game_data.setup_level()
        else:
            if game_data.score % 10 != 0:
                game_data.just_leveled_up = False

        # Draw vehicles
        screen.blit(assets['player_car'], game_data.player_rect)
        for enemy_rect, sprite, _ in game_data.enemy_cars:
            screen.blit(sprite, enemy_rect)

        # Display score and level
        score_text = assets['fonts']['score'].render(f"SCORE: {game_data.score}", True, COLORS['WHITE'])
        screen.blit(score_text, (20, 20))
        
        level_text = assets['fonts']['score'].render(f"LEVEL: {game_data.current_level + 1}", True, COLORS['WHITE'])
        screen.blit(level_text, (20, 60))

        # Only show manual panel if level is less than 2 (current_level < 1 means level 1)
        if game_data.current_level < 1:
            draw_manual_panel(screen, assets['fonts']['main'])

        rank = get_player_rank(player['uid'])
        draw_top_right_info(screen, assets['fonts']['main'], player['username'], game_data.score, player['score'], rank)

    if show_welcome:
        screen.fill((30, 30, 30))
        banner = assets['fonts']['large'].render(f"Welcome, {player['username']}!", True, COLORS['YELLOW'])
        screen.blit(banner, (WIDTH//2 - banner.get_width()//2, HEIGHT//2 - 60))
        info = assets['fonts']['main'].render("Press any key to continue...", True, COLORS['WHITE'])
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or (pygame.time.get_ticks() - welcome_timer > 1500):
                show_welcome = False
                difficulty_selection = True
        continue  # Skip rest of loop until welcome is done

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        pause_text = assets['fonts']['large'].render("PAUSED", True, COLORS['YELLOW'])
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 40))
        skip_text = assets['fonts']['main'].render("Press S to skip", True, COLORS['WHITE'])
        screen.blit(skip_text, (WIDTH//2 - skip_text.get_width()//2, HEIGHT//2 + 30))
        pygame.display.flip()
        clock.tick(10)
        continue  # Skip rest of game loop while paused
    
    if show_leaderboard:
        draw_leaderboard(screen, assets['fonts']['main'])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                show_leaderboard = False
        continue  # Skip rest of loop until leaderboard is done
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
