import pygame
import random
import sys

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
FONT_SIZE = 20
FPS = 15

# Colors (RGB tuples)
GREEN = (0, 255, 0)
BRIGHT_GREEN = (180, 255, 180)
RED = (255, 60, 60)
BLUE = (80, 180, 255)
COLOR_SCHEMES = [(GREEN, BRIGHT_GREEN), (RED, (255, 200, 200)), (BLUE, (180, 255, 255))]
color_index = 0

# Characters used (Mix of ASCII and Katakana-like)
CHARS = list("ﾊﾐﾋｰｳｼﾅﾓｸﾘｿｵﾁﾄ0123456789@#$%^&*abcdefghijklmnopqrstuvwxyzあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽァィゥェォッャュョヮヵヶ")

# Grid setup
COLUMNS = WIDTH // FONT_SIZE
rows = HEIGHT // FONT_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Rain FX")
font = pygame.font.SysFont("Courier", FONT_SIZE, bold=True)
clock = pygame.time.Clock()

# Each column has its own vertical position and speed
drops = [random.randint(-rows, 0) for _ in range(COLUMNS)]

# Trail buffer (transparent surface for fading)
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                color_index = (color_index + 1) % len(COLOR_SCHEMES)

    # Fade effect
    trail_surface.fill((0, 0, 0, 25))  # Low alpha = long-lasting trails
    screen.blit(trail_surface, (0, 0))

    for i in range(COLUMNS):
        x = i * FONT_SIZE
        y = drops[i] * FONT_SIZE
        head_color, tail_color = COLOR_SCHEMES[color_index]

        # Draw tail character
        char = random.choice(CHARS)
        char_surface = font.render(char, True, tail_color)
        screen.blit(char_surface, (x, y))

        # Draw bright head character above (for glow)
        if drops[i] > 0:
            bright_char = random.choice(CHARS)
            bright_surface = font.render(bright_char, True, head_color)
            screen.blit(bright_surface, (x, y - FONT_SIZE))

        # Move drop
        drops[i] += 1
        if drops[i] * FONT_SIZE > HEIGHT or random.random() > 0.975:
            drops[i] = random.randint(-10, 0)  # Reset with random offset for async drops

    pygame.display.flip()
    clock.tick(FPS)
