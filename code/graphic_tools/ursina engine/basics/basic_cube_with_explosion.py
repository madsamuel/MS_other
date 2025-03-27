from ursina import *
import numpy as np
import os

# Particle system setup
number_of_particles = 1000  # keep this as low as possible
points = np.array([Vec3(0, 0, 0) for i in range(number_of_particles)])
directions = np.array([Vec3(random.random() - 0.5, random.random() - 0.5, random.random() - 0.5) * 0.05 for i in range(number_of_particles)])
frames = []

# Simulate the particles once and cache the positions in a list
for i in range(60):
    points += directions
    frames.append(copy(points))


class ParticleSystem(Entity):
    def __init__(self, **kwargs):
        super().__init__(model=Mesh(vertices=points, mode='point', static=False, render_points_in_3d=True, thickness=0.1), t=0, duration=1, **kwargs)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.t += time.dt
        if self.t >= self.duration:
            destroy(self)
            return

        self.model.vertices = frames[floor(self.t * 60)]
        self.model.generate()


def explode_cube():
    ParticleSystem(
        position=cube.world_position,
        color=color.random_color(),
        rotation_y=random.random() * 360
    )


app = Ursina()

# Create the cube entity
cube = Entity(
    model='cube',
    color=color.azure,
    scale=2,
    collider='box'
)

# Add instructions
instructions = Text(
    text="Use arrows to move. Click the cube to make it explode!",
    origin=(0, 0),
    position=(0, -0.45),
    background=True,
    scale=2
)

cube.on_click = explode_cube

def update():
    # Move the cube left and right, up and down with arrow keys
    if held_keys['right arrow']:
        cube.x += 5 * time.dt
    elif held_keys['left arrow']:
        cube.x -= 5 * time.dt
    elif held_keys['up arrow']:
        cube.y += 5 * time.dt
    elif held_keys['down arrow']:
        cube.y -= 5 * time.dt

# Add camera controls
EditorCamera()

app.run()
