import pygame
import random
import math
import sys

# --------------------
# Configuration
# --------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)

# For cinematic space explosions, we often use fiery colors (yellow/orange/red).
# But you can tweak or randomize as desired.
EXPLOSION_COLORS = [
    (255, 225, 100),  # bright yellowish
    (255, 180, 50),   # warm orange
    (255, 120, 40),   # deeper orange-red
    (255, 50, 20),    # red
]


class Particle:
    """
    Represents a single particle in an explosion.
    """
    def __init__(self, x, y):
        # Initial position
        self.x = x
        self.y = y

        # Random direction
        angle = random.uniform(0, 2 * math.pi)

        # Speed (in space, there's no drag by default, so it will keep going)
        speed = random.uniform(200, 400)  # px/s (pixels per second)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Particle size
        self.size = random.randint(4, 8)

        # Pick a random color from the palette
        self.color = random.choice(EXPLOSION_COLORS)

        # How long this particle “lives” in seconds
        self.lifetime = random.uniform(1.0, 1.5)

        # Track how much time has passed
        self.age = 0.0

    def update(self, dt):
        """
        Update the particle’s position and age.
        dt is the time elapsed in seconds since last frame.
        """
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Optionally, you could reduce speed over time to simulate losing energy
        # For a space-like effect, you might leave it constant or reduce minimally.
        # e.g., self.vx *= 0.98

    def draw(self, surface):
        """
        Draw the particle. We can also fade it out over time by adjusting alpha.
        """
        # Calculate an alpha factor (1.0 = fully opaque, 0.0 = fully transparent)
        alpha_factor = 1.0 - (self.age / self.lifetime)
        alpha = max(0, int(255 * alpha_factor))

        # Create a surface just for this particle so we can control its alpha
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Fill the surface with the particle’s color and alpha
        pygame.draw.circle(
            particle_surface,
            (*self.color, alpha),
            (self.size // 2, self.size // 2),
            self.size // 2
        )
        # Blit onto the main surface at (x, y)
        surface.blit(particle_surface, (self.x - self.size / 2, self.y - self.size / 2))

    def is_dead(self):
        """
        Check if this particle has exceeded its lifetime.
        """
        return self.age >= self.lifetime


class Explosion:
    """
    Manages a collection of particles that together form an explosion.
    """
    def __init__(self, x, y, num_particles=50):
        self.particles = [Particle(x, y) for _ in range(num_particles)]

        # Initial flash: You might draw a big white circle that shrinks
        # or quickly fades. We’ll keep it simple and rely on bright particles.

    def update(self, dt):
        """
        Update all particles, and remove any that have 'died'.
        """
        for p in self.particles:
            p.update(dt)

        # Remove dead particles
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        """
        Draw all particles.
        """
        for p in self.particles:
            p.draw(surface)

    def is_finished(self):
        """
        Returns True if no particles are left alive.
        """
        return len(self.particles) == 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Explosion Demo")

    clock = pygame.time.Clock()

    # Keep a list of ongoing explosions
    explosions = []

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS, dt in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Trigger an explosion at a random position
                    ex_x = random.randint(100, SCREEN_WIDTH - 100)
                    ex_y = random.randint(100, SCREEN_HEIGHT - 100)
                    explosions.append(Explosion(ex_x, ex_y, num_particles=80))

        # Update explosions
        for explosion in explosions:
            explosion.update(dt)

        # Remove finished explosions
        explosions = [ex for ex in explosions if not ex.is_finished()]

        # Rendering
        screen.fill(BLACK)  # Space background
        for explosion in explosions:
            explosion.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
