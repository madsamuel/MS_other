import pygame
import sys

# Game constants
WIDTH, HEIGHT = 640, 480
FPS = 60
GRAVITY = 0.6
JUMP_STRENGTH = -12
PIXEL_SIZE = 8

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
SKIN = (255, 224, 189)
YELLOW = (255, 255, 0)
CLEAR = None

# Simplified Mario Pixel Art (16x16 based on provided image)
mario_pixels = [
    [CLEAR, CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, BROWN, BROWN, BROWN, SKIN, SKIN, BLACK, SKIN, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, SKIN, BROWN, SKIN, SKIN, SKIN, BLACK, SKIN, SKIN, SKIN, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, SKIN, BROWN, BROWN, SKIN, SKIN, SKIN, BLACK, SKIN, SKIN, SKIN, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, BROWN, SKIN, SKIN, SKIN, SKIN, BLACK, BLACK, BLACK, BLACK, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, CLEAR, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, RED, RED, BLUE, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, RED, RED, RED, BLUE, RED, RED, BLUE, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, RED, RED, RED, BLUE, BLUE, BLUE, BLUE, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, RED, RED, BLUE, YELLOW, BLUE, BLUE, YELLOW, BLUE, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, CLEAR, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR, CLEAR, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, BROWN, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR, CLEAR, BROWN, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR],
]

# Generate Mario sprite from pixel data
def draw_mario_surface():
    surface = pygame.Surface((16 * PIXEL_SIZE, 16 * PIXEL_SIZE), pygame.SRCALPHA)
    for y, row in enumerate(mario_pixels):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(surface, color, (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
    return surface

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Pixel Art Clone")
clock = pygame.time.Clock()

# Platforms and player
ground_height = 40
platforms = [pygame.Rect(0, HEIGHT - ground_height, WIDTH, ground_height)]
player = pygame.Rect(100, HEIGHT - 100, 16 * PIXEL_SIZE, 16 * PIXEL_SIZE)
mario_surface = draw_mario_surface()
vel_y = 0
on_ground = False

# Game loop
running = True
while running:
    screen.fill((106, 150, 252))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5
    if keys[pygame.K_SPACE] and on_ground:
        vel_y = JUMP_STRENGTH
        on_ground = False

    # Gravity
    vel_y += GRAVITY
    player.y += int(vel_y)

    # Collision detection
    on_ground = False
    for plat in platforms:
        if player.colliderect(plat) and vel_y >= 0:
            player.bottom = plat.top
            vel_y = 0
            on_ground = True

    # Draw everything
    for plat in platforms:
        pygame.draw.rect(screen, (0, 200, 0), plat)
    screen.blit(mario_surface, player)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
