import pygame
import random
import sys
import os

pygame.init()

# -------------------
# 1. BASIC SETTINGS
# -------------------
BASE_PATH = os.path.dirname(__file__)

# Default resolution
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga Clone with Pause & Restart")

FPS = 60
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
RED   = (255,   0,   0)
GRAY  = (100, 100, 100)
GREEN = (  0, 255,   0)

# -------------------
# GAME SETTINGS
# -------------------
PLAYER_SPEED        = 5
BULLET_SPEED        = 7
ENEMY_BASE_SPEED    = 2   # We'll multiply this by a difficulty factor
ENEMY_SPEED         = ENEMY_BASE_SPEED  # Actual speed used each frame
ENEMY_DROP_INTERVAL = 30  # frames between spawns

# Difficulty factor (1.0 = easy, 1.25 = medium, 1.5 = hard)
difficulty_factor = 1.0

# -------------------
# BULLET IMAGES
# -------------------
# 1) Default bullet: a 5x10 white rectangle
bullet_image_default = pygame.Surface((5, 10), pygame.SRCALPHA)
bullet_image_default.fill(WHITE)

# 2) Banana bullet (banana.png)
banana_path = os.path.join(BASE_PATH, "banana.png")
if os.path.exists(banana_path):
    bullet_image_banana = pygame.image.load(banana_path).convert_alpha()
    # Optionally scale your banana if needed, e.g. to 20x20
    # bullet_image_banana = pygame.transform.scale(bullet_image_banana, (20,20))
else:
    # Fallback if banana.png not found
    bullet_image_banana = bullet_image_default

# 3) Rocket bullet (rocket.png)
rocket_path = os.path.join(BASE_PATH, "rocket.png")
if os.path.exists(rocket_path):
    bullet_image_rocket = pygame.image.load(rocket_path).convert_alpha()
    # Optionally scale your rocket if needed
    # bullet_image_rocket = pygame.transform.scale(bullet_image_rocket, (10,30))
else:
    # Fallback if rocket.png not found
    bullet_image_rocket = bullet_image_default

# We keep track of the *current* bullet image
bullet_image_current = bullet_image_default

# -------------------
# STARFIELD SETTINGS
# -------------------
STAR_COUNT = 100   # Number of stars
STAR_SPEED = 1     # Vertical scrolling speed of stars

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.brightness = random.randint(50, 255)
        self.blink_speed = random.uniform(1, 3)
        self.direction = random.choice([-1, 1])

    def update(self):
        self.y += STAR_SPEED
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

        self.brightness += self.direction * self.blink_speed
        if self.brightness >= 255:
            self.brightness = 255
            self.direction = -1
        elif self.brightness <= 50:
            self.brightness = 50
            self.direction = 1

stars = [Star() for _ in range(STAR_COUNT)]

def draw_stars():
    for star in stars:
        star.update()
        star_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
        star_surf.fill((255, 255, 255, int(star.brightness)))
        SCREEN.blit(star_surf, (star.x, star.y))

def reinit_stars():
    global stars
    stars.clear()
    for _ in range(STAR_COUNT):
        stars.append(Star())

# -------------------
# SPLASH SCREEN
# -------------------
def splash_screen():
    logo_path = os.path.join(BASE_PATH, "logo.png")
    logo_image = pygame.image.load(logo_path).convert_alpha()
    logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))

    font_button = pygame.font.SysFont(None, 30)

    start_btn = pygame.Rect(0, 0, 140, 40)
    start_btn.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)

    settings_btn = pygame.Rect(0, 0, 140, 40)
    settings_btn.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if start_btn.collidepoint(mouse_pos):
                    return "start"
                if settings_btn.collidepoint(mouse_pos):
                    return "settings"

        SCREEN.fill(BLACK)
        draw_stars()

        SCREEN.blit(logo_image, logo_rect)

        pygame.draw.rect(SCREEN, GRAY, start_btn)
        pygame.draw.rect(SCREEN, GRAY, settings_btn)

        start_text = font_button.render("Start Game", True, BLACK)
        settings_text = font_button.render("Settings", True, BLACK)

        SCREEN.blit(start_text, start_text.get_rect(center=start_btn.center))
        SCREEN.blit(settings_text, settings_text.get_rect(center=settings_btn.center))

        pygame.display.flip()

# -------------------
# SETTINGS SCREEN
# -------------------
def settings_screen():
    """
    Settings screen:
      - Resolution buttons
      - Difficulty slider (Easy/Medium/Hard)
      - Bullet type (Default / Banana / Rocket)
      - Back
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN
    global difficulty_factor
    global bullet_image_current

    font_title = pygame.font.SysFont(None, 50)
    font_button = pygame.font.SysFont(None, 30)

    title_text = font_title.render("Settings", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 240))

    # ----------------------------------------
    # 1. Resolution Buttons
    # ----------------------------------------
    btn_480 = pygame.Rect(0, 0, 160, 40)
    btn_480.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 140)

    btn_720 = pygame.Rect(0, 0, 160, 40)
    btn_720.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80)

    # ----------------------------------------
    # 2. Difficulty Slider
    # ----------------------------------------
    slider_width = 200
    slider_height = 5
    slider_x = SCREEN_WIDTH//2 - slider_width//2
    slider_y = SCREEN_HEIGHT//2 - 10

    stop_positions = [
        slider_x,                     # Easy
        slider_x + slider_width//2,   # Medium
        slider_x + slider_width       # Hard
    ]
    difficulty_stops = [
        (stop_positions[0], 1.0),   # Easy => factor=1.0
        (stop_positions[1], 1.25),  # Medium => factor=1.25
        (stop_positions[2], 1.5)    # Hard => factor=1.5
    ]
    difficulty_labels = ["Easy", "Medium", "Hard"]

    # Find which stop is selected right now
    current_stop_index = 0
    possible_factors = [1.0, 1.25, 1.5]
    best_diff = 999
    for i, f in enumerate(possible_factors):
        diff = abs(f - difficulty_factor)
        if diff < best_diff:
            best_diff = diff
            current_stop_index = i

    knob_size = 10
    knob_rect = pygame.Rect(0, 0, knob_size, knob_size)
    knob_rect.center = (stop_positions[current_stop_index], slider_y)

    # ----------------------------------------
    # 3. Bullet Type Buttons
    # ----------------------------------------
    # We'll have 3 buttons for bullet type: Default / Banana / Rocket
    bullet_btn_default = pygame.Rect(0,0,120,40)
    bullet_btn_default.center = (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 50)

    bullet_btn_banana = pygame.Rect(0,0,120,40)
    bullet_btn_banana.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)

    bullet_btn_rocket = pygame.Rect(0,0,120,40)
    bullet_btn_rocket.center = (SCREEN_WIDTH//2 + 80, SCREEN_HEIGHT//2 + 50)

    # ----------------------------------------
    # 4. Back Button
    # ----------------------------------------
    btn_back = pygame.Rect(0, 0, 100, 40)
    btn_back.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # 1) Resolution Buttons
                if btn_480.collidepoint(mouse_pos):
                    SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
                    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    reinit_stars()
                elif btn_720.collidepoint(mouse_pos):
                    SCREEN_WIDTH, SCREEN_HEIGHT = 720, 960
                    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    reinit_stars()

                # 2) Difficulty Slider
                if (slider_y - 20 <= mouse_pos[1] <= slider_y + 20):
                    # measure distances to each stop
                    closest_i = None
                    closest_dist = 999999
                    for i, (stop_x, factor) in enumerate(difficulty_stops):
                        dist = abs(mouse_pos[0] - stop_x)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_i = i
                    if closest_i is not None:
                        knob_rect.centerx = difficulty_stops[closest_i][0]
                        difficulty_factor = difficulty_stops[closest_i][1]

                # 3) Bullet Type Buttons
                if bullet_btn_default.collidepoint(mouse_pos):
                    bullet_image_current = bullet_image_default
                elif bullet_btn_banana.collidepoint(mouse_pos):
                    bullet_image_current = bullet_image_banana
                elif bullet_btn_rocket.collidepoint(mouse_pos):
                    bullet_image_current = bullet_image_rocket

                # 4) Back Button
                if btn_back.collidepoint(mouse_pos):
                    return

        SCREEN.fill(BLACK)
        draw_stars()

        # Draw title
        SCREEN.blit(title_text, title_rect)

        # Draw resolution buttons
        pygame.draw.rect(SCREEN, GRAY, btn_480)
        pygame.draw.rect(SCREEN, GRAY, btn_720)
        txt_480 = font_button.render("480 x 640", True, BLACK)
        txt_720 = font_button.render("720 x 960", True, BLACK)
        SCREEN.blit(txt_480, txt_480.get_rect(center=btn_480.center))
        SCREEN.blit(txt_720, txt_720.get_rect(center=btn_720.center))

        # Draw the slider track
        pygame.draw.rect(SCREEN, WHITE, (slider_x, slider_y - slider_height//2, slider_width, slider_height))
        # Draw the knob
        pygame.draw.circle(SCREEN, GREEN, knob_rect.center, knob_size//2)

        # Draw difficulty labels
        for i, label in enumerate(difficulty_labels):
            label_surf = font_button.render(label, True, WHITE)
            label_rect = label_surf.get_rect(midtop=(stop_positions[i], slider_y + 10))
            SCREEN.blit(label_surf, label_rect)

        # Draw bullet type buttons
        pygame.draw.rect(SCREEN, GRAY, bullet_btn_default)
        pygame.draw.rect(SCREEN, GRAY, bullet_btn_banana)
        pygame.draw.rect(SCREEN, GRAY, bullet_btn_rocket)
        txt_def = font_button.render("Default", True, BLACK)
        txt_ban = font_button.render("Banana",  True, BLACK)
        txt_roc = font_button.render("Rocket",  True, BLACK)
        SCREEN.blit(txt_def, txt_def.get_rect(center=bullet_btn_default.center))
        SCREEN.blit(txt_ban, txt_ban.get_rect(center=bullet_btn_banana.center))
        SCREEN.blit(txt_roc, txt_roc.get_rect(center=bullet_btn_rocket.center))

        # Draw back button
        pygame.draw.rect(SCREEN, GRAY, btn_back)
        txt_back = font_button.render("Back", True, BLACK)
        SCREEN.blit(txt_back, txt_back.get_rect(center=btn_back.center))

        pygame.display.flip()

# -------------------
# SPRITE CLASSES
# -------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h):
        super().__init__()
        player_image_path = os.path.join(BASE_PATH, "player_ship.png")
        original_image = pygame.image.load(player_image_path).convert_alpha()
        
        width, height = original_image.get_size()
        scaled_width = width // 4
        scaled_height = height // 4
        self.image = pygame.transform.scale(original_image, (scaled_width, scaled_height))
        
        self.rect = self.image.get_rect()
        # Place the ship near bottom-left (based on your code)
        # If you prefer bottom-center:
        # self.rect.centerx = screen_w // 2
        # self.rect.centery = screen_h - 60
        self.rect.centerx = screen_w // 4
        self.rect.centery = screen_h - 60
        
    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT] and self.rect.right < SCREEN.get_width():
            self.rect.x += PLAYER_SPEED
        if keys_pressed[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN] and self.rect.bottom < SCREEN.get_height():
            self.rect.y += PLAYER_SPEED

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Use whichever bullet image is currently selected
        global bullet_image_current
        self.image = bullet_image_current
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load the boss.png image
        enemy_image_path = os.path.join(BASE_PATH, "boss.png")
        boss_image = pygame.image.load(enemy_image_path).convert_alpha()
        
        # OPTIONAL: Scale the boss image if desired
        # boss_image = pygame.transform.scale(boss_image, (30, 30))

        self.image = boss_image
        self.rect = self.image.get_rect(topleft=(x, y))
        
    def update(self):
        actual_speed = ENEMY_BASE_SPEED * difficulty_factor
        self.rect.y += actual_speed
        if self.rect.top > SCREEN.get_height():
            self.kill()

# -------------------
# HELPER FUNCTIONS
# -------------------
def pause_screen():
    paused = True
    font_big = pygame.font.SysFont(None, 64)
    pause_text = font_big.render("PAUSED", True, WHITE)
    
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False

        SCREEN.fill(BLACK)
        draw_stars()
        
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(pause_text, text_rect)
        
        pygame.display.flip()
        clock.tick(15)

def game_over_screen(score):
    font_large = pygame.font.SysFont(None, 64)
    font_small = pygame.font.SysFont(None, 32)

    game_over_text = font_large.render("GAME OVER", True, RED)
    go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))

    restart_btn = pygame.Rect(0, 0, 120, 40)
    restart_btn.center = (SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2 + 120)

    quit_btn = pygame.Rect(0, 0, 120, 40)
    quit_btn.center = (SCREEN_WIDTH//2 + 70, SCREEN_HEIGHT//2 + 120)

    while True:
        SCREEN.fill(BLACK)
        draw_stars()
        
        SCREEN.blit(game_over_text, go_rect)
        SCREEN.blit(score_text, score_rect)

        pygame.draw.rect(SCREEN, GRAY, restart_btn)
        pygame.draw.rect(SCREEN, GRAY, quit_btn)

        restart_text = font_small.render("Restart", True, BLACK)
        quit_text = font_small.render("Quit", True, BLACK)

        SCREEN.blit(restart_text, restart_text.get_rect(center=restart_btn.center))
        SCREEN.blit(quit_text, quit_text.get_rect(center=quit_btn.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    if restart_btn.collidepoint(mouse_pos):
                        return True
                    if quit_btn.collidepoint(mouse_pos):
                        return False

# -------------------
# MAIN GAME LOOP
# -------------------
def run_game():
    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT)
    player_group = pygame.sprite.Group(player)
    bullet_group = pygame.sprite.Group()
    enemy_group  = pygame.sprite.Group()

    score = 0
    font = pygame.font.SysFont(None, 36)
    enemy_spawn_counter = 0
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullet_group.add(bullet)
                elif event.key == pygame.K_ESCAPE:
                    pause_screen()

        keys_pressed = pygame.key.get_pressed()

        player_group.update(keys_pressed)
        bullet_group.update()
        enemy_group.update()

        enemy_spawn_counter += 1
        if enemy_spawn_counter >= ENEMY_DROP_INTERVAL:
            enemy_spawn_counter = 0
            # Use the actual image size or a known size if scaled
            # For now, we keep 30 for the random range unless you scale boss.png differently
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = -30
            enemy = Enemy(x, y)
            enemy_group.add(enemy)

        hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, True)
        if hits:
            for _ in hits:
                score += 10

        if pygame.sprite.spritecollideany(player, enemy_group):
            running = False

        SCREEN.fill(BLACK)
        draw_stars()
        player_group.draw(SCREEN)
        bullet_group.draw(SCREEN)
        enemy_group.draw(SCREEN)

        score_text = font.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        pygame.display.flip()

    return score

# -------------------
# MAIN ENTRY POINT
# -------------------
def main():
    while True:
        choice = splash_screen()
        if choice == "quit":
            break
        elif choice == "settings":
            settings_screen()
            continue
        elif choice == "start":
            final_score = run_game()
            wants_restart = game_over_screen(final_score)
            if wants_restart:
                continue
            else:
                break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
