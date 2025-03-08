import pygame
import math
import sys

def main():
    pygame.init()

    # Start with a default window size
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Halftone Flower Pattern")

    clock = pygame.time.Clock()
    time_val = 0.0

    def draw_fade_overlay(surface, alpha=25):
        """
        Draw a translucent black overlay each frame so old frames fade out
        instead of clearing completely. 'alpha' is 0..255.
        """
        fade_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        fade_surf.fill((0, 0, 0, alpha))  # black overlay w/ alpha
        surface.blit(fade_surf, (0, 0))

    def draw_halftone_spiral_color(surface):
        """
        1) Halftone logic for circle size:
           - circle size depends on distance from center + a sine wave => wave_offset
        2) Spiral color logic:
           - circle color (in grayscale) determined by angle + time => 
             color_val = sin(angle*some_factor - time_val)
        """

        grid_size = 20
        rows = (surface.get_height() // grid_size) + 1
        cols = (surface.get_width() // grid_size) + 1

        center_x = surface.get_width() / 2
        center_y = surface.get_height() / 2

        # Calculate the max distance from center to any corner (for normalization)
        max_distance = math.sqrt(center_x**2 + center_y**2)

        for row in range(rows):
            for col in range(cols):
                # The center of this cell
                cx = col * grid_size
                cy = row * grid_size

                # Distance from screen center
                distance = math.sqrt((cx - center_x)**2 + (cy - center_y)**2)
                normalized_distance = distance / max_distance

                # HALFTONE WAVE OFFSET => influences circle SIZE & ALPHA
                wave_offset = math.sin(normalized_distance * 10 - time_val) * 0.5 + 0.5
                size = grid_size * wave_offset * 0.8
                alpha_value = int(wave_offset * 127)  # 0..127

                # SPIRAL COLOR LOGIC => influences circle COLOR (grayscale)
                # Compute angle from center in radians
                angle = math.atan2(cy - center_y, cx - center_x)
                # Use sine wave with angle & time to get color from black..white
                spiral_val = math.sin(angle * 5 - time_val)
                color_val = int((spiral_val * 0.5 + 0.5) * 255)  # 0..255

                # Create a small surface for each circle with partial alpha
                circle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(
                    circle_surf,
                    (color_val, color_val, color_val, alpha_value),  # grayscale + alpha
                    (int(size // 2), int(size // 2)),
                    int(size // 2)
                )

                # Blit so the circle is centered on (cx, cy)
                surface.blit(circle_surf, (cx - size // 2, cy - size // 2))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Trail effect: fade overlay
        draw_fade_overlay(screen, alpha=25)

        # Draw the grid of circles:
        # - circle size uses halftone wave
        # - circle color uses a spiral function
        draw_halftone_spiral_color(screen)

        # Increment time for animation
        time_val += 0.05

        # Flip the display
        pygame.display.flip()
        clock.tick(60)  # ~60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
