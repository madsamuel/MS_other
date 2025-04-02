import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import sys

# Global flags
window_open = True
step_requested = False

def on_close(event):
    global window_open
    window_open = False

def on_step(event):
    global step_requested
    step_requested = True

def count_neighbors_3d(grid, x, y, z):
    nx, ny, nz = grid.shape
    count = 0
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == 0 and dy == 0 and dz == 0:
                    continue
                nx_pos = (x + dx) % nx
                ny_pos = (y + dy) % ny
                nz_pos = (z + dz) % nz
                count += grid[nx_pos, ny_pos, nz_pos]
    
    return count

def next_generation_3d(grid):
    survival_min, survival_max = 4, 8
    birth_min, birth_max = 3, 8

    nx, ny, nz = grid.shape
    new_grid = np.zeros((nx, ny, nz), dtype=int)

    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                neighbors = count_neighbors_3d(grid, x, y, z)
                if grid[x, y, z] == 1:
                    if survival_min <= neighbors <= survival_max:
                        new_grid[x, y, z] = 1
                else:
                    if birth_min <= neighbors <= birth_max:
                        new_grid[x, y, z] = 1
    return new_grid

def main():
    global window_open, step_requested

    nx, ny, nz = 20, 20, 20
    grid = np.random.choice([0, 1], size=(nx, ny, nz), p=[0.8, 0.2])
    
    # Matplotlib setup
    plt.ion()
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection='3d')
    fig.canvas.mpl_connect('close_event', on_close)

    # Add a "Step" button
    button_ax = plt.axes([0.4, 0.02, 0.2, 0.05])
    step_button = Button(button_ax, 'Step')
    step_button.on_clicked(on_step)

    generation = 0

    while window_open:
        if not step_requested:
            plt.pause(0.05)
            continue

        step_requested = False
        ax.clear()

        living_cells = np.argwhere(grid == 1)
        if living_cells.size > 0:
            xs, ys, zs = living_cells[:, 0], living_cells[:, 1], living_cells[:, 2]
            ax.scatter(xs, ys, zs, marker='o')

        ax.set_xlim(0, nx)
        ax.set_ylim(0, ny)
        ax.set_zlim(0, nz)
        ax.set_title(f"3D Game of Life (Toroidal) - Generation {generation}")

        plt.draw()

        grid = next_generation_3d(grid)
        generation += 1

    plt.ioff()
    plt.close(fig)
    sys.exit()

if __name__ == "__main__":
    main()
