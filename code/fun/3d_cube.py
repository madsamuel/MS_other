import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation

def create_small_cube(ax, position, size):
    """Create a small cube at a given position with a given size."""
    x, y, z = position
    r = [x, x, x+size, x+size, x, x, x+size, x+size]
    g = [y, y+size, y+size, y, y, y+size, y+size, y]
    b = [z, z, z, z, z+size, z+size, z+size, z+size]

    verts = [[r[0], g[0], b[0]],
             [r[1], g[1], b[1]],
             [r[2], g[2], b[2]],
             [r[3], g[3], b[3]],
             [r[4], g[4], b[4]],
             [r[5], g[5], b[5]],
             [r[6], g[6], b[6]],
             [r[7], g[7], b[7]]]

    faces = [[verts[j] for j in [0, 1, 2, 3]],
             [verts[j] for j in [4, 5, 6, 7]],
             [verts[j] for j in [0, 1, 5, 4]],
             [verts[j] for j in [2, 3, 7, 6]],
             [verts[j] for j in [1, 2, 6, 5]],
             [verts[j] for j in [4, 7, 3, 0]]]

    ax.add_collection3d(Poly3DCollection(faces, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

def create_large_cube(ax, size, num_cubes):
    """Create a large cube composed of smaller cubes."""
    small_cube_size = size / num_cubes
    for i in range(num_cubes):
        for j in range(num_cubes):
            for k in range(num_cubes):
                position = (i * small_cube_size, j * small_cube_size, k * small_cube_size)
                create_small_cube(ax, position, small_cube_size)

def update(num, ax, angle):
    """Update the rotation of the cube."""
    ax.view_init(30, angle)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create a large cube composed of smaller cubes
create_large_cube(ax, size=10, num_cubes=3)

# Set the limits of the plot
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])
ax.set_zlim([0, 10])

# Set the labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Create an animation
ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 360, 2), fargs=(ax, ), interval=50)

plt.show()
