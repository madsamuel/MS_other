import numpy as np
import matplotlib.pyplot as plt
import sys

# Global flag indicating whether the figure is still open
window_open = True

def on_close(event):
    """
    Matplotlib callback for when the figure window is closed.
    """
    global window_open
    window_open = False

def count_neighbors_3d(grid, x, y, z):
    nx, ny, nz = grid.shape
    count = 0
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == 0 and dy == 0 and dz == 0:
                    continue  # Skip the cell itself
                nx_pos = x + dx
                ny_pos = y + dy
                nz_pos = z + dz
                
                if 0 <= nx_pos < nx and 0 <= ny_pos < ny and 0 <= nz_pos < nz:
                    count += grid[nx_pos, ny_pos, nz_pos]
                    
    return count

def next_generation_3d(grid):
    nx, ny, nz = grid.shape
    new_grid = np.zeros((nx, ny, nz), dtype=int)
    
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                alive_neighbors = count_neighbors_3d(grid, x, y, z)
                
                if grid[x, y, z] == 1:
                    # Survival
                    if alive_neighbors == 2 or alive_neighbors == 3:
                        new_grid[x, y, z] = 1
                else:
                    # Birth
                    if alive_neighbors == 3:
                        new_grid[x, y, z] = 1
                        
    return new_grid

def main():
    global window_open
    
    # Grid size
    nx, ny, nz = 8, 8, 8
    # Random init
    grid = np.random.choice([0, 1], size=(nx, ny, nz), p=[0.5, 0.5])
    generations = 30
    
    # Set up interactive plotting
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    # Attach the on_close callback to detect when the window is closed
    fig.canvas.mpl_connect('close_event', on_close)
    
    for gen in range(generations):
        # If the window was closed, break out of the loop
        if not window_open:
            break

        ax.clear()
        
        living_cells = np.argwhere(grid == 1)
        if living_cells.size > 0:
            xs, ys, zs = living_cells[:, 0], living_cells[:, 1], living_cells[:, 2]
            ax.scatter(xs, ys, zs, marker='o')
        
        ax.set_xlim(0, nx)
        ax.set_ylim(0, ny)
        ax.set_zlim(0, nz)
        ax.set_title(f"3D Game of Life - Generation {gen}")
        
        plt.draw()
        
        # If the window is closed during pause, we handle it gracefully
        try:
            plt.pause(0.5)
        except:
            # If pause fails (window closed), exit the loop
            break
        
        # Next generation
        grid = next_generation_3d(grid)

    # Turn off interactive mode and close
    plt.ioff()
    plt.close(fig)
    sys.exit()

if __name__ == "__main__":
    main()
