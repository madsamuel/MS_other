import pygame
import random
import sys
import threading
import tkinter as tk
from tkinter import colorchooser

# Setup for tkinter
root = tk.Tk()
root.withdraw()

pygame.init()
clock = pygame.time.Clock()

# Screen setup
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Matrix GPU-Accelerated")

# Initial Colors
BLACK = (0, 0, 0)
HEAD_COLOR = (180, 255, 180)
CHAR_COLOR_BASE = [0, 255, 70]  # Mutable for threading

# Font setup
FONT_SIZE = 20
FONT = pygame.font.SysFont("ms mincho", FONT_SIZE, bold=True)
columns = WIDTH // FONT_SIZE

# Slimmed character pool for speed
characters = [chr(i) for i in range(33, 127)] + [chr(code) for code in range(0x30A0, 0x30F0, 4)]

# Drops and trails
drops = [random.randint(-20, 0) for _ in range(columns)]
trail_lengths = [random.randint(10, 30) for _ in range(columns)]
brightness_levels = list(range(0, 256, 25))

# Lazy cache for performance
char_surfaces = {}

def get_char_surface(char, brightness, base_color, head=False):
    key = (char, brightness if not head else 999)
    if key in char_surfaces:
        return char_surfaces[key]
    
    if head:
        color = HEAD_COLOR
    else:
        factor = brightness / 255.0
        color = tuple(int(c * factor) for c in base_color)
    surf = FONT.render(char, True, color)
    char_surfaces[key] = surf
    return surf

# Fade surface
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.set_alpha(40)
fade_surface.fill(BLACK)

def open_color_picker():
    rgb_color, _ = colorchooser.askcolor(title="Choose Matrix Color")
    if rgb_color:
        CHAR_COLOR_BASE[:] = list(map(int, rgb_color))
        char_surfaces.clear()

running = True
while running:
    screen.blit(fade_surface, (0, 0))

    for i in range(columns):
        x = i * FONT_SIZE
        y = drops[i] * FONT_SIZE
        char = random.choice(characters)

        screen.blit(get_char_surface(char, 999, CHAR_COLOR_BASE, head=True), (x, y))

        for t in range(1, trail_lengths[i]):
            fade_y = y - t * FONT_SIZE
            if fade_y < 0:
                continue
            brightness = max(0, 255 - t * (255 // trail_lengths[i]))
            brightness = brightness_levels[brightness // 25]
            trail_char = random.choice(characters)
            surf = get_char_surface(trail_char, brightness, CHAR_COLOR_BASE)
            screen.blit(surf, (x, fade_y))

        drops[i] += 1
        if y > HEIGHT or random.random() > 0.975:
            drops[i] = random.randint(-20, 0)

    pygame.display.flip()
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            threading.Thread(target=open_color_picker, daemon=True).start()

pygame.quit()
sys.exit()

