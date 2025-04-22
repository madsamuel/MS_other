import pygame
import random
import sys

# Initialize
pygame.init()
clock = pygame.time.Clock()

# Screen setup
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Matrix Rain")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)

# Font setup
FONT_SIZE = 20
FONT = pygame.font.SysFont("Consolas", FONT_SIZE)
columns = WIDTH // FONT_SIZE

# Matrix characters per column
drops = [random.randint(-20, 0) for _ in range(columns)]

def draw_matrix():
    screen.fill(BLACK)
    for i in range(len(drops)):
        char = chr(random.randint(33, 126))
        char_surface = FONT.render(char, True, GREEN)

        x = i * FONT_SIZE
        y = drops[i] * FONT_SIZE

        # Draw bright head
        screen.blit(char_surface, (x, y))

        # Optional trail effect
        trail_char = chr(random.randint(33, 126))
        trail_surface = FONT.render(trail_char, True, DARK_GREEN)
        screen.blit(trail_surface, (x, y - FONT_SIZE))

        # Update drop position
        drops[i] += 1
        if y > HEIGHT or random.random() > 0.975:
            drops[i] = random.randint(-20, 0)

# Main loop
running = True
while running:
    clock.tick(10)
    draw_matrix()
    pygame.display.flip()

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

pygame.quit()
sys.exit()
