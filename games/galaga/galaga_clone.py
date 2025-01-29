import pygame
import random
import sys
import os

pygame.init()

# -------------------
# 1. BASIC SETTINGS
# -------------------
BASE_PATH = os.path.dirname(__file__)

SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga Clone with Pause & Restart")

FPS = 60
clock = pygame.time.Clock()

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
RED   = (255,   0,   0)
GRAY  = (100, 100, 100)

# Game Settings
PLAYER_SPEED       = 5
BULLET_SPEED       = 7
ENEMY_SPEED        = 2
ENEMY_DROP_INTERVAL = 30  # frames between enemy spawns
PLAYER_START_X     = SCREEN_WIDTH // 2
PLAYER_START_Y     = SCREEN_HEIGHT - 60

# -------------------
# 2. SPLASH SCREEN
# -------------------
def splash_screen():
    """
    Displays the initial splash screen with a logo and two buttons:
    'Start Game' and 'Settings'.
    Returns one of: "start", "settings", or "quit".
    """
    # Load the logo image
    logo_path = os.path.join(BASE_PATH, "logo.png")
    logo_image = pygame.image.load(logo_path).convert_alpha()
    logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))

    # Fonts
    font_title = pygame.font.SysFont(None, 60)
    font_button = pygame.font.SysFont(None, 30)

    # Buttons
    start_btn = pygame.Rect(0, 0, 140, 40)
    start_btn.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)

    settings_btn = pygame.Rect(0, 0, 140, 40)
    settings_btn.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110)

    # Main loop for splash screen
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

        # Draw background
        SCREEN.fill(BLACK)

        # Draw the logo
        SCREEN.blit(logo_image, logo_rect)

        # Draw the buttons
        pygame.draw.rect(SCREEN, GRAY, start_btn)
        pygame.draw.rect(SCREEN, GRAY, settings_btn)

        start_text = font_button.render("Start Game", True, BLACK)
        settings_text = font_button.render("Settings", True, BLACK)

        SCREEN.blit(start_text, start_text.get_rect(center=start_btn.center))
        SCREEN.blit(settings_text, settings_text.get_rect(center=settings_btn.center))

        pygame.display.flip()

def settings_screen():
    """
    A simple placeholder for a Settings screen.
    Press any key or click to return to the splash screen.
    """
    font_big = pygame.font.SysFont(None, 50)
    text = font_big.render("Settings Screen", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # Return to main => eventually leads to quit
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # Go back to splash

        SCREEN.fill(BLACK)
        SCREEN.blit(text, text_rect)
        pygame.display.flip()

# -------------------
# 3. SPRITE CLASSES
# -------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load the original player image
        player_image_path = os.path.join(BASE_PATH, "player_ship.png")
        original_image = pygame.image.load(player_image_path).convert_alpha()
        
        # Scale the player image to 50% of its original width/height
        width, height = original_image.get_size()
        scaled_width = width // 2
        scaled_height = height // 2
        self.image = pygame.transform.scale(original_image, (scaled_width, scaled_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = (PLAYER_START_X, PLAYER_START_Y)
        
    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        if keys_pressed[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += PLAYER_SPEED

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        
    def update(self):
        self.rect.y += ENEMY_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# -------------------
# 4. HELPER FUNCTIONS
# -------------------
def pause_screen():
    """
    Display a pause message and wait until the user presses ESC again to resume.
    """
    paused = True
    font_big = pygame.font.SysFont(None, 64)
    pause_text = font_big.render("PAUSED", True, WHITE)
    text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Press ESC again to resume
                if event.key == pygame.K_ESCAPE:
                    paused = False

        # Optional: draw a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)  # alpha level for semi-transparency
        overlay.fill(BLACK)
        SCREEN.blit(overlay, (0, 0))
        
        SCREEN.blit(pause_text, text_rect)
        
        pygame.display.flip()
        clock.tick(15)  # limit loop speed during pause

def game_over_screen(score):
    """
    Display a 'Game Over' screen with the final score and a Restart button.
    Returns True if the player wants to restart, False if the player quits.
    """
    font_large = pygame.font.SysFont(None, 64)
    font_small = pygame.font.SysFont(None, 32)

    game_over_text = font_large.render("GAME OVER", True, RED)
    go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))

    # Restart button
    restart_btn = pygame.Rect(0, 0, 120, 40)
    restart_btn.center = (SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2 + 120)

    # Quit button
    quit_btn = pygame.Rect(0, 0, 120, 40)
    quit_btn.center = (SCREEN_WIDTH//2 + 70, SCREEN_HEIGHT//2 + 120)

    while True:
        SCREEN.fill(BLACK)
        
        SCREEN.blit(game_over_text, go_rect)
        SCREEN.blit(score_text, score_rect)

        # Draw the buttons
        pygame.draw.rect(SCREEN, GRAY, restart_btn)
        pygame.draw.rect(SCREEN, GRAY, quit_btn)

        restart_text = font_small.render("Restart", True, BLACK)
        quit_text = font_small.render("Quit", True, BLACK)

        SCREEN.blit(restart_text, restart_text.get_rect(center=restart_btn.center))
        SCREEN.blit(quit_text, quit_text.get_rect(center=quit_btn.center))

        pygame.display.flip()

        # Event handling for the Game Over screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    if restart_btn.collidepoint(mouse_pos):
                        return True   # Restart
                    if quit_btn.collidepoint(mouse_pos):
                        return False  # Quit

# -------------------
# 5. MAIN GAME LOOP
# -------------------
def run_game():
    """
    Run the main game loop once, returning the final score when game ends.
    """
    # Create sprite groups
    player = Player()
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
                    # Shoot bullet
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullet_group.add(bullet)
                elif event.key == pygame.K_ESCAPE:
                    # Pause
                    pause_screen()

        keys_pressed = pygame.key.get_pressed()

        # Update sprites
        player_group.update(keys_pressed)
        bullet_group.update()
        enemy_group.update()

        # Spawn enemies
        enemy_spawn_counter += 1
        if enemy_spawn_counter >= ENEMY_DROP_INTERVAL:
            enemy_spawn_counter = 0
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = -30
            enemy = Enemy(x, y)
            enemy_group.add(enemy)

        # Check collisions: Bullets -> Enemies
        hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, True)
        if hits:
            for _ in hits:
                score += 10

        # Check collisions: Player -> Enemies
        if pygame.sprite.spritecollideany(player, enemy_group):
            running = False

        # Drawing
        SCREEN.fill(BLACK)
        player_group.draw(SCREEN)
        bullet_group.draw(SCREEN)
        enemy_group.draw(SCREEN)

        score_text = font.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        pygame.display.flip()

    return score

# -------------------
# 6. MAIN ENTRY POINT
# -------------------
def main():
    """
    The main entry point. 
    1) Show splash screen first.
    2) If Start => run the game loop, then show game over screen.
    3) If Settings => show settings screen, then return to splash.
    4) If Quit => exit.
    """
    while True:
        choice = splash_screen()
        if choice == "quit":
            break
        elif choice == "settings":
            settings_screen()
            # After returning from settings, go back to splash_screen again
            continue
        elif choice == "start":
            final_score = run_game()
            wants_restart = game_over_screen(final_score)
            if wants_restart:
                # If user clicked "Restart" at game over, jump directly into another game
                continue
            else:
                # If user clicked "Quit" at game over, exit to OS
                break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
