import pygame
import random
import math
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
ENEMY_DROP_INTERVAL = 30  # frames between spawns

# Difficulty factor (1.0 = easy, 1.25 = medium, 1.5 = hard)
difficulty_factor = 1.0

# -------------------
# BULLET IMAGES
# -------------------
bullet_image_default = pygame.Surface((5, 10), pygame.SRCALPHA)
bullet_image_default.fill(WHITE)

banana_path = os.path.join(BASE_PATH, "banana.png")
if os.path.exists(banana_path):
    bullet_image_banana = pygame.image.load(banana_path).convert_alpha()
else:
    bullet_image_banana = bullet_image_default

rocket_path = os.path.join(BASE_PATH, "rocket.png")
if os.path.exists(rocket_path):
    bullet_image_rocket = pygame.image.load(rocket_path).convert_alpha()
else:
    bullet_image_rocket = bullet_image_default

bullet_image_current = bullet_image_default

# -------------------
# STARFIELD SETTINGS
# -------------------
STAR_COUNT = 100
STAR_SPEED = 1

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

# ---------------------------------------------------
# SETTINGS SCREEN - Recalculate positions each loop
# ---------------------------------------------------
def settings_screen():
    """
    Settings screen:
      - Resolution buttons
      - Difficulty slider (Easy/Medium/Hard)
      - Projectile slider (Default / Banana / Rocket)
      - Back
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN
    global difficulty_factor, bullet_image_current

    font_title = pygame.font.SysFont(None, 50)
    font_button = pygame.font.SysFont(None, 30)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # Check resolution buttons
                if btn_480.collidepoint(mouse_pos):
                    SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
                    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    reinit_stars()
                elif btn_720.collidepoint(mouse_pos):
                    SCREEN_WIDTH, SCREEN_HEIGHT = 720, 960
                    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    reinit_stars()

                # Check difficulty slider
                if (slider_y - 20 <= mouse_pos[1] <= slider_y + 20):
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

                # Check projectile slider
                if (bullet_slider_y - 20 <= mouse_pos[1] <= bullet_slider_y + 20):
                    closest_i = None
                    closest_dist = 999999
                    for i, stop_x in enumerate(bullet_stop_positions):
                        dist = abs(mouse_pos[0] - stop_x)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_i = i
                    if closest_i is not None:
                        bullet_knob_rect.centerx = bullet_stop_positions[closest_i]
                        bullet_image_current = bullet_images[closest_i]

                # Back button
                if btn_back.collidepoint(mouse_pos):
                    return

        # --------------------------------------------
        # Recalculate the positions each frame
        # (so if the resolution changed above,
        #  the new pass will recalc everything)
        # --------------------------------------------
        title_text = font_title.render("Settings", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 280))

        # Buttons for resolution
        btn_480 = pygame.Rect(0, 0, 160, 40)
        btn_480.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 180)

        btn_720 = pygame.Rect(0, 0, 160, 40)
        btn_720.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120)

        # Difficulty slider
        slider_width = 200
        slider_height = 5
        slider_x = SCREEN_WIDTH//2 - slider_width//2
        slider_y = SCREEN_HEIGHT//2 - 40

        stop_positions = [
            slider_x,
            slider_x + slider_width//2,
            slider_x + slider_width
        ]
        difficulty_stops = [
            (stop_positions[0], 1.0),
            (stop_positions[1], 1.25),
            (stop_positions[2], 1.5)
        ]
        difficulty_labels = ["Easy", "Medium", "Hard"]

        # Find which stop is currently selected
        possible_factors = [1.0, 1.25, 1.5]
        # find the closest factor
        best_diff = 999
        current_stop_index = 0
        for i, f in enumerate(possible_factors):
            diff = abs(f - difficulty_factor)
            if diff < best_diff:
                best_diff = diff
                current_stop_index = i

        knob_size = 10
        knob_rect = pygame.Rect(0, 0, knob_size, knob_size)
        knob_rect.center = (stop_positions[current_stop_index], slider_y)

        # Projectile slider
        bullet_slider_width = 200
        bullet_slider_height = 5
        bullet_slider_x = SCREEN_WIDTH//2 - bullet_slider_width//2
        bullet_slider_y = SCREEN_HEIGHT//2 + 30

        bullet_stop_positions = [
            bullet_slider_x,
            bullet_slider_x + bullet_slider_width//2,
            bullet_slider_x + bullet_slider_width
        ]
        bullet_images = [bullet_image_default, bullet_image_banana, bullet_image_rocket]
        bullet_labels = ["Default", "Banana", "Rocket"]

        # Check which bullet image is selected
        bullet_current_index = 0
        for i, bi in enumerate(bullet_images):
            if bi == bullet_image_current:
                bullet_current_index = i
                break

        bullet_knob_rect = pygame.Rect(0, 0, knob_size, knob_size)
        bullet_knob_rect.center = (bullet_stop_positions[bullet_current_index], bullet_slider_y)

        # Back button
        btn_back = pygame.Rect(0, 0, 100, 40)
        btn_back.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140)

        # --------------------------------------------
        # Draw everything
        # --------------------------------------------
        SCREEN.fill(BLACK)
        draw_stars()

        SCREEN.blit(title_text, title_rect)

        # Resolution buttons
        pygame.draw.rect(SCREEN, GRAY, btn_480)
        pygame.draw.rect(SCREEN, GRAY, btn_720)
        txt_480 = font_button.render("480 x 640", True, BLACK)
        txt_720 = font_button.render("720 x 960", True, BLACK)
        SCREEN.blit(txt_480, txt_480.get_rect(center=btn_480.center))
        SCREEN.blit(txt_720, txt_720.get_rect(center=btn_720.center))

        # Difficulty slider track & knob
        pygame.draw.rect(SCREEN, WHITE, (slider_x, slider_y - slider_height//2, slider_width, slider_height))
        pygame.draw.circle(SCREEN, GREEN, knob_rect.center, knob_size//2)
        # labels
        for i, label in enumerate(difficulty_labels):
            label_surf = font_button.render(label, True, WHITE)
            label_rect = label_surf.get_rect(midtop=(stop_positions[i], slider_y + 10))
            SCREEN.blit(label_surf, label_rect)

        # Projectile slider track & knob
        pygame.draw.rect(SCREEN, WHITE, (bullet_slider_x, bullet_slider_y - bullet_slider_height//2,
                                         bullet_slider_width, bullet_slider_height))
        pygame.draw.circle(SCREEN, GREEN, bullet_knob_rect.center, knob_size//2)
        for i, label in enumerate(bullet_labels):
            label_surf = font_button.render(label, True, WHITE)
            label_rect = label_surf.get_rect(midtop=(bullet_stop_positions[i], bullet_slider_y + 10))
            SCREEN.blit(label_surf, label_rect)

        # Back button
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
        # We'll place it near bottom-left per your code
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
        enemy_image_path = os.path.join(BASE_PATH, "boss.png")
        boss_image = pygame.image.load(enemy_image_path).convert_alpha()
        self.image = boss_image
        self.rect = self.image.get_rect(topleft=(x, y))
        
    def update(self):
        actual_speed = ENEMY_BASE_SPEED * difficulty_factor
        self.rect.y += actual_speed
        if self.rect.top > SCREEN.get_height():
            self.kill()

# -------------------
# EXPLOSION LOGIC
# -------------------
EXPLOSION_COLORS = [
    (255, 225, 100),  # bright yellowish
    (255, 180, 50),
    (255, 120, 40),
    (255, 50, 20),
]

class Particle:
    def __init__(self, x, y, speed_scale=1.0, size_scale=1.0):
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(200, 400) * speed_scale
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        base_size = random.randint(4, 8)
        self.size = int(base_size * size_scale)

        self.color = random.choice(EXPLOSION_COLORS)
        self.lifetime = random.uniform(1.0, 1.5)
        self.age = 0.0

        self.x = x
        self.y = y

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface):
        alpha_factor = 1.0 - (self.age / self.lifetime)
        alpha = max(0, int(255 * alpha_factor))

        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(
            particle_surface,
            (*self.color, alpha),
            (self.size // 2, self.size // 2),
            self.size // 2
        )
        surface.blit(particle_surface, (self.x - self.size/2, self.y - self.size/2))

    def is_dead(self):
        return self.age >= self.lifetime

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_size=30):
        super().__init__()
        self.image = pygame.Surface((1,1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x,y))

        base_count = 30
        scale_factor = enemy_size / 30.0
        num_particles = int(base_count * scale_factor)

        self.particles = [
            Particle(x, y, speed_scale=scale_factor, size_scale=scale_factor)
            for _ in range(num_particles)
        ]

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]
        if len(self.particles) == 0:
            self.kill()

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

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
    explosions_group = pygame.sprite.Group()

    score = 0
    font = pygame.font.SysFont(None, 36)
    enemy_spawn_counter = 0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

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

        # update explosions
        explosions_group.update(dt)

        # spawn enemies
        enemy_spawn_counter += 1
        if enemy_spawn_counter >= ENEMY_DROP_INTERVAL:
            enemy_spawn_counter = 0
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = -30
            enemy = Enemy(x, y)
            enemy_group.add(enemy)

        # bullet-enemy collisions
        hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, True)
        if hits:
            for bullet, enemies in hits.items():
                for dead_enemy in enemies:
                    score += 10
                    # spawn explosion at enemy location, scaled by enemy size
                    enemy_w = dead_enemy.rect.width
                    enemy_h = dead_enemy.rect.height
                    avg_size = (enemy_w + enemy_h) // 2
                    ex = Explosion(dead_enemy.rect.centerx, dead_enemy.rect.centery, avg_size)
                    explosions_group.add(ex)

        # player-enemy collisions
        if pygame.sprite.spritecollideany(player, enemy_group):
            running = False

        SCREEN.fill(BLACK)
        draw_stars()
        player_group.draw(SCREEN)
        bullet_group.draw(SCREEN)
        enemy_group.draw(SCREEN)

        # draw explosions
        for ex in explosions_group:
            ex.draw(SCREEN)

        score_text = font.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        pygame.display.flip()

    return score

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
