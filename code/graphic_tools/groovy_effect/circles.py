import pygame
import math
import sys

def main():
    pygame.init()

    # Start with a default window size
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Halftone Wave in Python")

    clock = pygame.time.Clock()
    time_val = 0.0

    # For the trailing effect, we draw a translucent black overlay each frame
    # so the older frames slowly fade out instead of clearing completely.
    def draw_fade_overlay(surface, alpha=25):
        fade_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        # RGBA -> black with an alpha value
        fade_surf.fill((0, 0, 0, alpha))
        surface.blit(fade_surf, (0, 0))

    def draw_halftone_wave(surface):
        grid_size = 20
        rows = (surface.get_height() // grid_size) + 1
        cols = (surface.get_width() // grid_size) + 1

        center_x = surface.get_width() / 2
        center_y = surface.get_height() / 2

        # Calculate the max distance from the center to any corner (for normalization)
        max_distance = math.sqrt(center_x**2 + center_y**2)

        for row in range(rows):
            for col in range(cols):
                # Pixel centers
                cx = col * grid_size
                cy = row * grid_size

                distance = math.sqrt((cx - center_x)**2 + (cy - center_y)**2)
                normalized_distance = distance / max_distance

                # Similar wave calculation from the original code
                wave_offset = math.sin(normalized_distance * 10 - time_val) * 0.5 + 0.5
                size = grid_size * wave_offset * 0.8

                # Set circle alpha to half of wave_offset => wave_offset * 0.5 => 0..0.5
                alpha_value = int(wave_offset * 127)

                # Draw a circle with partial alpha
                circle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(
                    circle_surf,
                    (255, 255, 255, alpha_value),  # White with alpha
                    (size // 2, size // 2),
                    int(size // 2)
                )
                # Center the circle on the grid point
                surface.blit(circle_surf, (cx - size // 2, cy - size // 2))

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Resize the screen surface accordingly
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Draw a translucent black overlay for the trailing effect
        draw_fade_overlay(screen, alpha=25)

        # Draw our halftone wave
        draw_halftone_wave(screen)

        # Increment time for the wave animation
        time_val += 0.05

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
