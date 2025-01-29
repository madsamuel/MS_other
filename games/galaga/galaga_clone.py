import pygame
import random
import sys
import os

# Get the absolute path to the folder containing this script
BASE_PATH = os.path.dirname(__file__)

# Initialize pygame
pygame.init()

# -------------------
# 1. BASIC SETTINGS
# -------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga Clone")

FPS = 60
clock = pygame.time.Clock()

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

# Game Settings
PLAYER_SPEED       = 5
BULLET_SPEED       = 7
ENEMY_SPEED        = 2
ENEMY_DROP_INTERVAL = 30  # frames between enemy spawns
PLAYER_START_X     = SCREEN_WIDTH // 2
PLAYER_START_Y     = SCREEN_HEIGHT - 60

# -------------------
# 2. SPRITE CLASSES
# -------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Construct the path to 'player_ship.png' in the same folder as this script
        player_image_path = os.path.join(BASE_PATH, "player_ship.png")
        self.image = pygame.image.load(player_image_path).convert_alpha()
        
        self.rect = self.image.get_rect()
        self.rect.center = (PLAYER_START_X, PLAYER_START_Y)
        
    def update(self, keys_pressed):
        # Move left
        if keys_pressed[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        # Move right
        if keys_pressed[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        # Move up
        if keys_pressed[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        # Move down
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
        # Remove the bullet if it goes off-screen
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
        # Remove enemy if it goes off-screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# -------------------
# 3. GROUPS & OBJECTS
# -------------------
player = Player()

# Sprite groups
player_group = pygame.sprite.Group(player)
bullet_group = pygame.sprite.Group()
enemy_group  = pygame.sprite.Group()

score = 0
font = pygame.font.SysFont(None, 36)

# Spawn timer to control enemy creation
enemy_spawn_counter = 0

# -------------------
# 4. MAIN GAME LOOP
# -------------------
def main():
    global score, enemy_spawn_counter
    running = True
    
    while running:
        clock.tick(FPS)  # Limit the frame rate
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Shoot bullet on spacebar
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullet_group.add(bullet)
        
        # Get pressed keys for movement
        keys_pressed = pygame.key.get_pressed()
        
        # Update player, bullets, and enemies
        player_group.update(keys_pressed)
        bullet_group.update()
        enemy_group.update()
        
        # Spawn a new enemy periodically
        enemy_spawn_counter += 1
        if enemy_spawn_counter >= ENEMY_DROP_INTERVAL:
            enemy_spawn_counter = 0
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = -30  # spawn off top of screen
            enemy = Enemy(x, y)
            enemy_group.add(enemy)
        
        # Collision detection:
        #  1. Bullets vs. Enemies
        hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, True)
        for _ in hits:
            score += 10
        
        #  2. Player vs. Enemies
        if pygame.sprite.spritecollideany(player, enemy_group):
            # In Galaga, you'd typically lose a life or end the game
            running = False
        
        # Draw everything
        SCREEN.fill(BLACK)
        player_group.draw(SCREEN)
        bullet_group.draw(SCREEN)
        enemy_group.draw(SCREEN)
        
        # Draw the score
        score_text = font.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))
        
        pygame.display.flip()
    
    # Game Over Screen
    game_over()

def game_over():
    # Simple "Game Over" loop
    go_font = pygame.font.SysFont(None, 64)
    go_text = go_font.render("GAME OVER", True, RED)
    go_rect = go_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    
    while True:
        SCREEN.fill(BLACK)
        SCREEN.blit(go_text, go_rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
