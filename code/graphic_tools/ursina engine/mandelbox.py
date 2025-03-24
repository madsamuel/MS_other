from ursina import *
from ursina.shaders import lit_with_shadows_shader
import math

app = Ursina()

camera.position = (0, 0, -100)
camera.look_at(Vec3(0, 0, 0))
window.color = color.black

DirectionalLight(y=2, z=-2, shadows=True)
scene.ambient_color = color.rgb(60, 60, 60)

mandelbox_root = Entity()

# Mandelbox constants
SCALE = 2.0   # s
RADIUS = 0.5  # r
FOLD = 1.0    # f
MAX_ITER = 10
THRESHOLD = 10

def box_fold(v: Vec3) -> Vec3:
    for i in range(3):
        if v[i] > 1.0:
            v[i] = 2.0 - v[i]
        elif v[i] < -1.0:
            v[i] = -2.0 - v[i]
    return v

def ball_fold(v: Vec3) -> Vec3:
    mag = v.length()
    if mag < RADIUS:
        v *= (1.0 / (RADIUS * RADIUS))
    elif mag < 1.0:
        v *= (1.0 / (mag * mag))
    return v

def mandelbox_escape(c: Vec3) -> bool:
    z = c
    for _ in range(MAX_ITER):
        z = box_fold(z)
        z *= FOLD
        z = ball_fold(z)
        z = z * SCALE + c
        if z.length() > THRESHOLD:
            return False
    return True

def build_mandelbox(res=12, box_size=30):
    step = box_size / res
    offset = box_size / 2

    for x in range(res):
        for y in range(res):
            for z in range(res):
                # Map grid to space [-1.5, 1.5] in each axis
                cx = x * step - offset
                cy = y * step - offset
                cz = z * step - offset
                point = Vec3(cx, cy, cz) / offset  # normalize to roughly [-1,1]

                if mandelbox_escape(point):
                    Entity(
                        model='cube',
                        parent=mandelbox_root,
                        position=Vec3(cx, cy, cz),
                        scale=step * 0.9,
                        color=color.azure,
                        shader=lit_with_shadows_shader,
                        double_sided=True,
                        collider=None
                    )

# Build Mandelbox fractal
build_mandelbox(res=12, box_size=30)

def update():
    mandelbox_root.rotation_y += 20 * time.dt
    mandelbox_root.rotation_x += 10 * time.dt

app.run()
