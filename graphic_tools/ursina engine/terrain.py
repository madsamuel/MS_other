from ursina import *
import random
import math
import numpy as np
from perlin_noise import PerlinNoise

class Terrain(Entity):
    def __init__(self, size=20, scale=1.5, height_multiplier=4, **kwargs):
        super().__init__(**kwargs)

        self.size = size
        self.scale = scale
        self.height_multiplier = height_multiplier

        # Generate Perlin noise
        noise = PerlinNoise(octaves=4, seed=random.randint(0, 100))

        # Create terrain vertices
        verts = []
        tris = []
        uv_coords = []

        for z in range(size):
            for x in range(size):
                height = noise([x/size, z/size]) * height_multiplier
                verts.append(Vec3((x - size//2) * scale, height, (z - size//2) * scale))  # Center terrain
                uv_coords.append((x / size, z / size))

        # Generate triangle indices for mesh
        for z in range(size - 1):
            for x in range(size - 1):
                i = x + z * size
                tris.extend([i, i+size, i+1, i+1, i+size, i+size+1])

        # Create mesh
        self.model = Mesh(vertices=verts, triangles=tris, uvs=uv_coords, mode='triangle', thickness=1)
        self.texture = 'grass'
        self.collider = 'mesh'
        self.color = color.green


class RotatingCamera(Entity):
    def __init__(self, target, radius=20, speed=10):
        super().__init__()
        self.target = target
        self.radius = radius
        self.angle = 0
        self.speed = speed
        self.y = 15  # Camera height
        self.update_rotation()

    def update_rotation(self):
        """Updates the camera's position to orbit around the terrain."""
        self.angle += time.dt * self.speed  # Smooth rotation
        self.x = self.target.x + self.radius * math.cos(math.radians(self.angle))
        self.z = self.target.z + self.radius * math.sin(math.radians(self.angle))
        self.look_at(self.target.position)

    def update(self):
        """Automatically updates the camera every frame."""
        self.update_rotation()


def main():
    app = Ursina()

    window.color = color.black  # Background

    # Generate 3D terrain
    terrain = Terrain(size=30, scale=1.8, height_multiplier=6)
    terrain.y = -2  # Lower terrain to be centered

    # Rotating camera around terrain
    rotating_camera = RotatingCamera(target=terrain, radius=30, speed=10)

    # Lighting
    directional_light = DirectionalLight(color=color.white, shadows=True)
    directional_light.look_at(Vec3(1, -1, 1))

    ambient_light = AmbientLight(color=color.rgba(255,255,255,100))

    app.run()


if __name__ == '__main__':
    main()
