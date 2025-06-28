import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle

def project_to_poincare(z, scale=4.0):
    """Projects a complex number from the Euclidean plane to the Poincaré disk."""
    magnitude = np.abs(z)
    if np.isclose(magnitude, 0):
        return 0j
    # tanh maps [0, inf) to [0, 1), scaling the Euclidean plane
    new_magnitude = np.tanh(magnitude / scale)
    return (z / magnitude) * new_magnitude

def plot_projected_tiling(grid_size=10, scale=4.0):
    """
    Generates a tiling by projecting a Euclidean grid of triangles
    into the Poincaré disk, mimicking the user's reference image.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.add_patch(Circle((0, 0), 1, fill=False, edgecolor='black', lw=1))

    # Loop through each square in the Euclidean grid
    for i in range(-grid_size, grid_size):
        for j in range(-grid_size, grid_size):
            # Define the 5 key points for a square: 4 corners, 1 center
            center = complex(i + 0.5, j + 0.5)
            corners = [
                complex(i, j),
                complex(i + 1, j),
                complex(i + 1, j + 1),
                complex(i, j + 1)
            ]

            # The 4 triangles of the square connect the center to two adjacent corners
            for k in range(4):
                p1 = center
                p2 = corners[k]
                p3 = corners[(k + 1) % 4]
                
                # Project the triangle's vertices into the disk
                proj_verts = [project_to_poincare(p, scale) for p in [p1, p2, p3]]
                
                # Convert complex numbers to (x,y) coordinates for plotting
                plot_verts = [[v.real, v.imag] for v in proj_verts]
                
                # Determine the color based on a checkerboard pattern
                is_square_even = (i + j) % 2 == 0
                is_triangle_even = k % 2 == 0
                
                if is_square_even:
                    color = 'black' if is_triangle_even else 'white'
                else:
                    color = 'white' if is_triangle_even else 'black'
                
                # Draw the projected triangle
                ax.add_patch(Polygon(plot_verts, facecolor=color, edgecolor='black', lw=0.2))

    plt.title("Projection of Euclidean Tiling into Poincaré Disk")
    plt.show()

if __name__ == '__main__':
    # grid_size controls how many tiles are drawn
    # scale controls the density of the tiles near the center
    plot_projected_tiling(grid_size=12, scale=5.0)
