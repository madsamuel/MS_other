from ursina import *
from ursina.shaders import lit_with_shadows_shader
import math

app = Ursina()

# Camera & Scene Setup
camera.position = (0, 0, -20)
camera.look_at(Vec3(0, 0, 0))
window.color = color.black

# Lighting (angled to improve highlights & shadows)
light = DirectionalLight(x=1, y=2, z=-3, shadows=True)
scene.ambient_color = color.rgb(20, 20, 20)

# Entity that holds the whole fractal
koch_root = Entity()

# Parameters
DEPTH = 3              # Fractal depth
THICKNESS = 0.5        # Z-thickness
SIZE = 8               # Triangle size
SEGMENT_HEIGHT = 0.2   # Y-thickness per segment

def koch_snowflake(p1, p2, depth):
    if depth == 0:
        return [p1, p2]

    dx = (p2[0] - p1[0]) / 3
    dy = (p2[1] - p1[1]) / 3

    a = (p1[0] + dx, p1[1] + dy)
    b = (p1[0] + 2 * dx, p1[1] + 2 * dy)

    angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    length = math.sqrt(dx**2 + dy**2)
    peak = (
        (a[0] + b[0]) / 2 + math.sin(angle) * length * math.sqrt(3)/6,
        (a[1] + b[1]) / 2 - math.cos(angle) * length * math.sqrt(3)/6
    )

    return (
        koch_snowflake(p1, a, depth - 1) +
        koch_snowflake(a, peak, depth - 1)[1:] +
        koch_snowflake(peak, b, depth - 1)[1:] +
        koch_snowflake(b, p2, depth - 1)[1:]
    )

def generate_snowflake_2_5d(size=SIZE, depth=DEPTH, thickness=THICKNESS):
    h = size * math.sqrt(3) / 2
    p1 = (-size / 2, -h / 3)
    p2 = (size / 2, -h / 3)
    p3 = (0, 2 * h / 3)

    edge1 = koch_snowflake(p1, p2, depth)
    edge2 = koch_snowflake(p2, p3, depth)
    edge3 = koch_snowflake(p3, p1, depth)

    full_path = edge1[:-1] + edge2[:-1] + edge3  # avoid duplicated points

    for i in range(len(full_path) - 1):
        start = full_path[i]
        end = full_path[i + 1]
        mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        length = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        angle = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0]))

        # Give each segment a slight hue variation
        segment_color = color.hsv(210 + i % 20, 0.6, 1.0)

        Entity(
            model='cube',
            parent=koch_root,
            position=Vec3(mid[0], mid[1], 0),
            scale=Vec3(length, SEGMENT_HEIGHT, thickness),
            rotation=Vec3(0, 0, angle),
            color=segment_color,
            shader=lit_with_shadows_shader,
            double_sided=True
        )

generate_snowflake_2_5d()

def update():
    koch_root.rotation_y += 15 * time.dt
    koch_root.rotation_z += 10 * time.dt

app.run()
