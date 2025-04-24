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
pygame.display.set_caption("Matrix Rain Enhanced")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 70)
BRIGHT_GREEN = (180, 255, 180)

# Font setup
FONT_SIZE = 20
FONT = pygame.font.SysFont("ms mincho", FONT_SIZE, bold=True)
columns = WIDTH // FONT_SIZE

# Character pool: Katakana + ASCII
katakana = [chr(code) for code in range(0x30A0, 0x30FF)]
ascii_chars = [chr(i) for i in range(33, 127)]
characters = katakana + ascii_chars

# Drops and brightness trail
drops = [random.randint(-20, 0) for _ in range(columns)]
trail_lengths = [random.randint(10, 30) for _ in range(columns)]

# Create surface for trail fading
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.set_alpha(40)
fade_surface.fill(BLACK)

# Main loop
running = True
while running:
    screen.blit(fade_surface, (0, 0))  # fade effect
    for i in range(columns):
        x = i * FONT_SIZE
        y = drops[i] * FONT_SIZE
        char = random.choice(characters)

        # Draw main bright character
        head = FONT.render(char, True, BRIGHT_GREEN)
        screen.blit(head, (x, y))

        # Draw trail
        for t in range(1, trail_lengths[i]):
            fade_y = y - t * FONT_SIZE
            if fade_y < 0:
                continue
            brightness = max(0, 255 - t * (255 // trail_lengths[i]))
            trail_char = random.choice(characters)
            trail_surface = FONT.render(trail_char, True, (0, brightness, 0))
            screen.blit(trail_surface, (x, fade_y))

        # Update drop position
        drops[i] += 1
        if y > HEIGHT or random.random() > 0.975:
            drops[i] = random.randint(-20, 0)

    # Display and event loop
    pygame.display.flip()
    clock.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

pygame.quit()
sys.exit()
