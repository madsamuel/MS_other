from ursina import *
from ursina.shaders import lit_with_shadows_shader
import math
import time

app = Ursina()
window.color = color.black
camera.position = (0, 0, -10)
camera.look_at(Vec3(0, 0, 0))

# Lighting setup
DirectionalLight(y=2, z=-3, shadows=True)
scene.ambient_color = color.rgb(30, 30, 30)

# Constants
MAX_STEPS = 100
MAX_DIST = 100.0
SURF_DIST = 0.001
PI = math.pi
TAU = 2 * math.pi

koch_root = Entity()

def rot2d(v, angle):
    s, c = math.sin(angle), math.cos(angle)
    return Vec2(v.x * c - v.y * s, v.x * s + v.y * c)

def N(angle):
    return Vec2(math.sin(angle), math.cos(angle))

def koch(uv):
    uv.x = abs(uv.x)
    angle = 5.0 / 6.0 * PI
    n = N(angle)
    
    uv.y += math.tan(angle) * 0.5
    d = (uv - Vec2(0.5, 0)).dot(n)
    uv -= max(0.0, d) * n * 2.0

    scale = 1.0
    n = N(2.0 / 3.0 * PI)
    uv.x += 0.5
    for _ in range(4):
        uv *= 3
        scale *= 3
        uv.x -= 1.5
        uv.x = abs(uv.x)
        uv.x -= 0.5
        d = uv.dot(n)
        uv -= min(0.0, d) * n * 2.0

    uv /= scale
    return uv

def get_dist(p, t):
    angle = t * 0.2
    # Rotate the xz components
    xz = rot2d(Vec2(p.x, p.z), angle)
    p = Vec3(xz.x, p.y, xz.y)
    
    k1 = koch(Vec2(Vec2(p.x, p.z).length(), p.y))
    k2 = koch(Vec2(Vec2(p.y, p.z).length(), p.x))
    k3 = koch(Vec2(Vec2(p.x, p.y).length(), p.z))
    
    d = max(k1.x, max(k2.x, k3.x))
    d = lerp(d, p.length() - 0.5, 0.5)
    return d

def ray_march(ro, rd, t):
    total_dist = 0.0
    for _ in range(MAX_STEPS):
        p = ro + rd * float(total_dist)  # Multiply vector by float on the right.
        d = get_dist(p, t)
        total_dist += d
        if total_dist > MAX_DIST or abs(d) < SURF_DIST:
            break
    return total_dist

def get_normal(p, t):
    e = 0.001
    dx = get_dist(p, t) - get_dist(p - Vec3(e, 0, 0), t)
    dy = get_dist(p, t) - get_dist(p - Vec3(0, e, 0), t)
    dz = get_dist(p, t) - get_dist(p - Vec3(0, 0, e), t)
    return Vec3(dx, dy, dz).normalized()

def get_ray_dir(uv, eye, target, zoom):
    f = (target - eye).normalized()
    r = f.cross(Vec3(0, 1, 0)).normalized()
    u = r.cross(f)
    c = f * zoom
    # Multiply vector * float, not float * vector.
    i = c + r * float(uv.x) + u * float(uv.y)
    return i.normalized()

voxels = []
res = 60

def build_koch():
    t = time.time()
    for y in range(-res//2, res//2):
        for x in range(-res//2, res//2):
            uv = Vec2(x, y) / res * 2
            ro = Vec3(0, 3, -3)
            
            angle_y = -0.3 * PI + 1
            angle_x = -0.3 * TAU
            ry = rot2d(Vec2(ro.y, ro.z), angle_y)
            rx = rot2d(Vec2(ro.x, ro.z), angle_x)
            ro.y, ro.z = ry.x, ry.y
            ro.x, ro.z = rx.x, rx.y
            
            rd = get_ray_dir(uv, ro, Vec3(0, 0, 0), 3.0)
            dist = ray_march(ro, rd, t)
            
            if dist < MAX_DIST:
                # Use rd * float(dist) so the vector is on the left.
                p = ro + rd * float(dist)
                normal = get_normal(p, t)
                brightness = max(0.1, normal.dot(Vec3(1, 2, 3).normalized()))
                voxel = Entity(
                    model='cube',
                    position=p,
                    scale=0.05,
                    color=color.color(210, 0.9, brightness),
                    parent=koch_root,
                    shader=lit_with_shadows_shader
                )
                voxels.append(voxel)

build_koch()

def update():
    koch_root.rotation_y += 10 * time.dt
    koch_root.rotation_x += 5 * time.dt

app.run()
