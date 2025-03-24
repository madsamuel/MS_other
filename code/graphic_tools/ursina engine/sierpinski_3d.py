from ursina import *
from ursina.mesh_importer import Mesh
from ursina.shaders import lit_with_shadows_shader
import random

app = Ursina()
camera.position = (0, 5, -60)
camera.look_at(Vec3(0, 0, 0))
window.color = color.black

# Add a directional light to illuminate the model
DirectionalLight(y=2, z=-3, shadows=True)
# Optionally, add some ambient light
scene.ambient_color = color.rgb(50, 50, 50)

def create_tetrahedron(v0, v1, v2, v3, color=color.white):
    vertices = [v0, v1, v2, v3]
    triangles = [
        (0, 1, 2),  # Base
        (0, 1, 3),
        (1, 2, 3),
        (2, 0, 3)
    ]
    mesh = Mesh(
        vertices=[vertices[i] for tri in triangles for i in tri],
        triangles=[i for i in range(12)],
        mode='triangle'
    )
    mesh.generate_normals()  # Generate normals for proper shading
    # Add double_sided=True to render both sides of each face.
    return Entity(model=mesh, color=color, collider=None, shader=lit_with_shadows_shader, double_sided=True)

def midpoint(p1, p2):
    return (p1 + p2) / 2

def sierpinski(v0, v1, v2, v3, depth):
    if depth == 0:
        # Each tetrahedron is given a random HSV color.
        tetra = create_tetrahedron(v0, v1, v2, v3, color.hsv(random.uniform(0,1), 1, 1))
        tetra_list.append(tetra)
        return

    # Calculate midpoints of each edge
    m01 = midpoint(v0, v1)
    m02 = midpoint(v0, v2)
    m03 = midpoint(v0, v3)
    m12 = midpoint(v1, v2)
    m13 = midpoint(v1, v3)
    m23 = midpoint(v2, v3)

    # Recursively build 4 smaller tetrahedra (omitting the central one)
    sierpinski(v0, m01, m02, m03, depth - 1)
    sierpinski(m01, v1, m12, m13, depth - 1)
    sierpinski(m02, m12, v2, m23, depth - 1)
    sierpinski(m03, m13, m23, v3, depth - 1)

# Define the main tetrahedron vertices
size = 5
v0 = Vec3(0, size, 0)
v1 = Vec3(-size, -size, size)
v2 = Vec3(size, -size, size)
v3 = Vec3(0, -size, -size)

# Store all tetrahedra for animation
tetra_list = []
sierpinski(v0, v1, v2, v3, depth=2)  # Adjust depth (2–4 is good)

def update():
    # Spin animation: rotate each tetrahedron over time
    for t in tetra_list:
        t.rotation_y += 20 * time.dt
        t.rotation_x += 10 * time.dt

app.run()
