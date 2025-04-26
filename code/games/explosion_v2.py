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

# Enhanced explosion colors with gradients and more variety
EXPLOSION_COLORS = [
    (255, 225, 100),  # bright yellowish
    (255, 180, 50),   # warm orange
    (255, 120, 40),   # deeper orange-red
    (255, 50, 20),    # red
    (200, 50, 255),   # purple
    (50, 200, 255),   # cyan
]

class Particle:
    """
    Represents a single particle in an explosion.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(200, 400)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(4, 8)
        self.color = random.choice(EXPLOSION_COLORS)
        self.lifetime = random.uniform(1.0, 1.5)
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.98  # Simulate drag
        self.vy *= 0.98

    def draw(self, surface):
        alpha_factor = 1.0 - (self.age / self.lifetime)
        alpha = max(0, int(255 * alpha_factor))
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(
            particle_surface,
            (*self.color, alpha),
            (self.size // 2, self.size // 2),
            self.size // 2
        )
        surface.blit(particle_surface, (self.x - self.size / 2, self.y - self.size / 2))

    def is_dead(self):
        return self.age >= self.lifetime

class Explosion:
    """
    Manages a collection of particles that together form an explosion.
    """
    def __init__(self, x, y, num_particles=50):
        self.particles = [Particle(x, y) for _ in range(num_particles)]

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def is_finished(self):
        return len(self.particles) == 0

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Enhanced Explosion Demo")

    clock = pygame.time.Clock()
    explosions = []

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    ex_x = random.randint(100, SCREEN_WIDTH - 100)
                    ex_y = random.randint(100, SCREEN_HEIGHT - 100)
                    explosions.append(Explosion(ex_x, ex_y, num_particles=100))

        for explosion in explosions:
            explosion.update(dt)

        explosions = [ex for ex in explosions if not ex.is_finished()]

        screen.fill(BLACK)
        for explosion in explosions:
            explosion.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()