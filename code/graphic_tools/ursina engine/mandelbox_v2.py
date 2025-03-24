from ursina import *
from ursina.shaders import lit_with_shadows_shader
import numpy as np
import math

app = Ursina()

# Camera setup
camera.position = (0, 0, -100)
camera.look_at(Vec3(0, 0, 0))
window.color = color.black

# Lighting
DirectionalLight(y=2, z=-2, shadows=True)
scene.ambient_color = color.rgb(60, 60, 60)

# Root container to rotate the whole fractal
mandelbox_root = Entity()

# === Mandelbox Parameters ===
SCALE = 2.0
RADIUS = 0.5
ITERATIONS = 10
THRESHOLD = 0.03
RESOLUTION = 10  # increase for more detail (warning: gets heavy)

def mandelbox_distance_estimator(c, scale=SCALE, iterations=ITERATIONS, r=RADIUS):
    z = c.copy()
    dr = 1.0
    for _ in range(iterations):
        # Box fold
        for i in range(3):
            if z[i] > 1.0:
                z[i] = 2.0 - z[i]
            elif z[i] < -1.0:
                z[i] = -2.0 - z[i]

        mag = np.linalg.norm(z)
        # Ball fold
        if mag < r:
            z *= (1.0 / (r * r))
            dr *= (1.0 / (r * r))
        elif mag < 1.0:
            z /= (mag * mag)
            dr /= (mag * mag)

        # Scale and offset
        z = z * scale + c
        dr = dr * abs(scale) + 1.0

    return np.linalg.norm(z) / abs(dr)

def generate_mandelbox(res=RESOLUTION, size=30, threshold=THRESHOLD):
    step = size / res
    offset = size / 2

    for x in range(res):
        for y in range(res):
            for z in range(res):
                # Normalize to roughly [-1.5, 1.5]
                nx = x * step - offset
                ny = y * step - offset
                nz = z * step - offset
                point = np.array([nx, ny, nz]) / offset

                distance = mandelbox_distance_estimator(point)
                if distance < threshold:
                    Entity(
                        model='cube',
                        parent=mandelbox_root,
                        position=Vec3(nx, ny, nz),
                        scale=step * 0.9,
                        color=color.azure,
                        shader=lit_with_shadows_shader,
                        double_sided=True,
                        collider=None
                    )

# Generate the fractal
generate_mandelbox()

def update():
    mandelbox_root.rotation_y += 20 * time.dt
    mandelbox_root.rotation_x += 10 * time.dt

app.run()
