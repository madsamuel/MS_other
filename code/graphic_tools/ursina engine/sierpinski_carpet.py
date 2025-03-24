from ursina import *
import math

app = Ursina()

camera.position = (0, 150, -60)
camera.look_at(Vec3(0, 0, 0))
window.color = color.black

DirectionalLight(y=2, z=-2, shadows=True)
scene.ambient_color = color.rgb(60, 60, 60)

# Load custom shader
blue_gradient_shader = Shader(language=Shader.GLSL, vertex='blue_gradient.shader', fragment='blue_gradient.shader')

sponge = Entity()
MIN_CUBE_SIZE = 0.3

def create_cube(center: Vec3, size: float):
    if size < MIN_CUBE_SIZE or math.isnan(size) or math.isinf(size):
        return

    Entity(
        parent=sponge,
        model='cube',
        position=center,
        scale=size,
        shader=blue_gradient_shader,
        double_sided=True,
        collider=None
    )

def menger(center: Vec3, size: float, depth: int):
    if depth == 0 or size < MIN_CUBE_SIZE:
        create_cube(center, size)
        return

    new_size = size / 3
    offsets = [-new_size, 0, new_size]

    for dx in offsets:
        for dy in offsets:
            for dz in offsets:
                if (dx == 0 and dy == 0) or (dx == 0 and dz == 0) or (dy == 0 and dz == 0):
                    continue

                new_center = center + Vec3(dx, dy, dz)
                menger(new_center, new_size, depth - 1)

initial_center = Vec3(0, 0, 0)
initial_size = 30
menger_depth = 2

menger(initial_center, initial_size, menger_depth)

def update():
    sponge.rotation_y += 20 * time.dt
    sponge.rotation_x += 10 * time.dt

app.run()
