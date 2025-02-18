import pygame
import math
import sys
import numpy as np

def main():
    pygame.init()

    # Start with a default window size, resizable.
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Spiral Effect in Python")

    clock = pygame.time.Clock()
    time_val = 0.0  # Tracks the progression of the spiral over time.

    # Helper function to fade previously drawn frames (for trailing effect).
    def draw_fade_overlay(surface, alpha=25):
        """
        Draw a translucent black rectangle over the screen to fade out old frames.
        alpha=25 means mild fade each frame (0-255 range).
        """
        fade_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        fade_surf.fill((0, 0, 0, alpha))  # black with alpha
        surface.blit(fade_surf, (0, 0))

    def draw_spiral(surface, t):
        """
        Draws an expanding spiral based on time t.
        Increases the maximum angle as t grows, so the spiral expands frame-by-frame.
        """
        cx, cy = surface.get_width() // 2, surface.get_height() // 2
        scale = 2.0         # Adjust to change how quickly the spiral expands.
        step = 0.1          # Angular step between each point on the spiral.
        max_angle = t       # The spiral grows with time.

        # Loop from angle = 0 up to time_val (in radians).
        angle = 0.0
        while angle < max_angle:
            # Convert polar (angle, r) to cartesian (x, y).
            r = scale * angle
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)

            # Draw a small circle with partial alpha for each step.
            # Example color: white (255,255,255) with alpha=127.
            circle_color = (255, 255, 255, 127)

            circle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, circle_color, (3, 3), 3)
            surface.blit(circle_surf, (x - 3, y - 3))

            angle += step

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Re-create the screen surface with the new size
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Fade previous frame: black with some transparency for the trailing effect
        draw_fade_overlay(screen, alpha=25)

        # Draw the spiral, time_val defines how large it becomes
        draw_spiral(screen, time_val)

        # Increment time_val for continuous growth
        time_val += 0.05

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # ~60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
