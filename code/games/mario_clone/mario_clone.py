import pygame
import sys

# Initialize
pygame.init()
WIDTH, HEIGHT = 640, 480
FPS = 60
GRAVITY = 0.6
JUMP_STRENGTH = -12

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Mario Clone")
clock = pygame.time.Clock()

# Colors
BLUE = (106, 150, 252)
BROWN = (139, 69, 19)
GREEN = (0, 200, 0)

# Pixel art placeholder for Mario (16x16 blocky style)
mario_surface = pygame.Surface((32, 32))
mario_surface.fill((255, 0, 0))
pygame.draw.rect(mario_surface, (255, 200, 0), (8, 8, 16, 16))  # face

# Level ground
ground_height = 40
platforms = [pygame.Rect(0, HEIGHT - ground_height, WIDTH, ground_height)]

# Player
player = pygame.Rect(100, HEIGHT - 100, 32, 32)
vel_y = 0
on_ground = False

# Main game loop
running = True
while running:
    screen.fill(BLUE)
    keys = pygame.key.get_pressed()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Horizontal movement
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5

    # Jumping
    if keys[pygame.K_SPACE] and on_ground:
        vel_y = JUMP_STRENGTH
        on_ground = False

    # Gravity
    vel_y += GRAVITY
    player.y += int(vel_y)

    # Collision
    on_ground = False
    for plat in platforms:
        if player.colliderect(plat) and vel_y >= 0:
            player.bottom = plat.top
            vel_y = 0
            on_ground = True

    # Draw platforms
    for plat in platforms:
        pygame.draw.rect(screen, GREEN, plat)

    # Draw player
    screen.blit(mario_surface, player)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
