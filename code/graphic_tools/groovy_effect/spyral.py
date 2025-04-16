import pygame
import math
import sys

def main():
    pygame.init()

    # Start with a default window size
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Halftone Wave + Single Spiral Color")

    clock = pygame.time.Clock()
    time_val = 0.0

    def draw_fade_overlay(surface, alpha=25):
        """
        Draw a translucent black overlay so old frames fade out
        instead of clearing completely. alpha is 0..255.
        """
        fade_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        fade_surf.fill((0, 0, 0, alpha))  # black overlay with alpha
        surface.blit(fade_surf, (0, 0))

    def draw_halftone_spiral_color(surface):
        """
        1) Circle size (wave_offset) from the halftone wave logic.
        2) Single spiral color: we compute color_val from 'angle + distance' minus time_val,
           so there's a single swirling arm from the center outward.
        """

        grid_size = 20
        rows = (surface.get_height() // grid_size) + 1
        cols = (surface.get_width() // grid_size) + 1

        center_x = surface.get_width() / 2
        center_y = surface.get_height() / 2

        # Max distance from center to a corner (for normalizing wave)
        max_distance = math.sqrt(center_x**2 + center_y**2)

        for row in range(rows):
            for col in range(cols):
                cx = col * grid_size
                cy = row * grid_size

                # Distance & angle from center
                distance = math.sqrt((cx - center_x)**2 + (cy - center_y)**2)
                angle = math.atan2(cy - center_y, cx - center_x)

                # ---------------------------
                # 1) HALFTONE WAVE => SIZE
                # ---------------------------
                normalized_dist = distance / max_distance
                wave_offset = math.sin(normalized_dist * 10 - time_val) * 0.5 + 0.5
                size = grid_size * wave_offset * 0.8
                alpha_value = int(wave_offset * 127)  # 0..127

                # ---------------------------
                # 2) SPIRAL COLOR => GRAYSCALE
                # ---------------------------
                # The spiral factor is (distance + angle) minus time,
                # so color shifts in a single spiral arm outward from center.
                spiral_factor = distance * 0.5 + angle - time_val
                spiral_val = math.sin(spiral_factor) * 0.5 + 0.5  # range 0..1
                color_val = int(spiral_val * 255)                  # grayscale in 0..255

                # Create circle surf with partial alpha
                circle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(
                    circle_surf,
                    (color_val, color_val, color_val, alpha_value),
                    (int(size // 2), int(size // 2)),
                    int(size // 2)
                )
                # Blit so the circle is centered
                surface.blit(circle_surf, (cx - size // 2, cy - size // 2))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Fading trail effect
        draw_fade_overlay(screen, alpha=25)

        # Draw grid of circles (halftone size + single spiral color)
        draw_halftone_spiral_color(screen)

        # Increment time for animation
        time_val += 0.05

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
