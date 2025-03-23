from ursina import *
from ursina.mesh_importer import Mesh

app = Ursina()
camera.position = (0, 5, -20)
camera.look_at(Vec3(0, 0, 0))
window.color = color.black

# Define a single tetrahedron using 4 vertices and faces
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
    mesh.generate_normals()
    return Entity(model=mesh, color=color, collider=None)

# Midpoint helper
def midpoint(p1, p2):
    return (p1 + p2) / 2

# Recursive Sierpinski builder
def sierpinski(v0, v1, v2, v3, depth):
    if depth == 0:
        tetra = create_tetrahedron(v0, v1, v2, v3, color.hsv(random.uniform(0,1), 1, 1))
        tetra_list.append(tetra)
        return

    # Midpoints of edges
    m01 = midpoint(v0, v1)
    m02 = midpoint(v0, v2)
    m03 = midpoint(v0, v3)
    m12 = midpoint(v1, v2)
    m13 = midpoint(v1, v3)
    m23 = midpoint(v2, v3)

    # Recurse into 4 smaller tetrahedra (omit center one for hollow look)
    sierpinski(v0, m01, m02, m03, depth - 1)
    sierpinski(m01, v1, m12, m13, depth - 1)
    sierpinski(m02, m12, v2, m23, depth - 1)
    sierpinski(m03, m13, m23, v3, depth - 1)

# Main tetrahedron vertices (equilateral)
size = 5
v0 = Vec3(0, size, 0)
v1 = Vec3(-size, -size, size)
v2 = Vec3(size, -size, size)
v3 = Vec3(0, -size, -size)

# Store all pieces for animation
tetra_list = []
sierpinski(v0, v1, v2, v3, depth=2)  # Change depth for more detail (2–4 is good)

# Optional: spin animation
def update():
    for t in tetra_list:
        t.rotation_y += 20 * time.dt  # rotate all
        t.rotation_x += 10 * time.dt  # tilt

app.run()
