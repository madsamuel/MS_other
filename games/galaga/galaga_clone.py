import pygame
import random
import sys

pygame.init()

# -------------------
# 1. BASIC SETTINGS
# -------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga Clone with Restart & High Score")

FPS = 60
clock = pygame.time.Clock()

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
GRAY  = (100, 100, 100)

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED  = 2
ENEMY_DROP_INTERVAL = 30  # frames between enemy spawns

PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - 60

# Global High Score
high_score = 0


# -------------------
# 2. SPRITE CLASSES
# -------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
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
# 3. HELPER FUNCTIONS
# -------------------
def init_game():
    """Initialize or reset game objects and variables."""
    global player, player_group, bullet_group, enemy_group, score, enemy_spawn_counter
    
    player = Player()
    # Sprite groups
    player_group = pygame.sprite.Group(player)
    bullet_group = pygame.sprite.Group()
    enemy_group  = pygame.sprite.Group()

    score = 0
    enemy_spawn_counter = 0
    
    return (player_group, bullet_group, enemy_group)

def run_game():
    """One round of the main game loop. Returns the final score."""
    global score, enemy_spawn_counter
    
    # Use the already initialized groups
    running = True
    font = pygame.font.SysFont(None, 36)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Shoot bullet on spacebar
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullet_group.add(bullet)

        # Get pressed keys for movement
        keys_pressed = pygame.key.get_pressed()
        
        # Update player, bullets, enemies
        player_group.update(keys_pressed)
        bullet_group.update()
        enemy_group.update()
        
        # Spawn enemies periodically
        enemy_spawn_counter += 1
        if enemy_spawn_counter >= ENEMY_DROP_INTERVAL:
            enemy_spawn_counter = 0
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = -30  # spawn above screen
            enemy = Enemy(x, y)
            enemy_group.add(enemy)
        
        # Bullet-Enemy collisions
        hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, True)
        for _ in hits:
            score += 10
        
        # Player-Enemy collisions
        if pygame.sprite.spritecollideany(player, enemy_group):
            # End the game on collision
            running = False
        
        # Drawing
        SCREEN.fill(BLACK)
        player_group.draw(SCREEN)
        bullet_group.draw(SCREEN)
        enemy_group.draw(SCREEN)
        
        # Draw the score
        score_text = font.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))
        
        pygame.display.flip()
    
    # Return final score from this round
    return score

def game_over(final_score):
    """
    Display a 'Game Over' screen with the final score and a Restart button.
    Returns True if the player wants to restart, False if the player quits.
    """
    global high_score
    
    # Update high score if needed
    if final_score > high_score:
        high_score = final_score

    font_large = pygame.font.SysFont(None, 64)
    font_small = pygame.font.SysFont(None, 32)

    game_over_text = font_large.render("GAME OVER", True, RED)
    go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    
    score_text = font_small.render(f"Score: {final_score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
    
    high_score_text = font_small.render(f"High Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45))

    # Restart button
    restart_btn = pygame.Rect(0, 0, 120, 40)
    restart_btn.center = (SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2 + 120)

    # Quit button
    quit_btn = pygame.Rect(0, 0, 120, 40)
    quit_btn.center = (SCREEN_WIDTH//2 + 70, SCREEN_HEIGHT//2 + 120)

    while True:
        SCREEN.fill(BLACK)
        
        # Draw "GAME OVER" and score texts
        SCREEN.blit(game_over_text, go_rect)
        SCREEN.blit(score_text, score_rect)
        SCREEN.blit(high_score_text, high_score_rect)

        # Draw buttons
        pygame.draw.rect(SCREEN, GRAY, restart_btn)
        pygame.draw.rect(SCREEN, GRAY, quit_btn)

        restart_text = font_small.render("Restart", True, BLACK)
        quit_text = font_small.render("Quit", True, BLACK)

        SCREEN.blit(restart_text, 
                    restart_text.get_rect(center=restart_btn.center))
        SCREEN.blit(quit_text, 
                    quit_text.get_rect(center=quit_btn.center))

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
                        # Player clicked "Restart"
                        return True
                    if quit_btn.collidepoint(mouse_pos):
                        # Player clicked "Quit"
                        return False


def main():
    """
    Continuously run the game. After a game-over, either restart or quit based on user choice.
    """
    while True:
        # Initialize/reset game data
        init_game()
        # Run a single playthrough
        final_score = run_game()
        # Show Game Over screen
        wants_restart = game_over(final_score)
        if not wants_restart:
            break  # Exit the whole program
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
