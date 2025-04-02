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
    """
    Count the number of alive neighbors around cell (x, y, z) in the 3D grid.
    Uses toroidal/wrap-around boundaries so edges connect to the opposite sides.
    """
    nx, ny, nz = grid.shape
    count = 0
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == 0 and dy == 0 and dz == 0:
                    continue  # Skip the cell itself
                nx_pos = (x + dx) % nx
                ny_pos = (y + dy) % ny
                nz_pos = (z + dz) % nz
                count += grid[nx_pos, ny_pos, nz_pos]
    
    return count

def next_generation_3d(grid):
    """
    Compute the next generation of the 3D Game of Life based on the current grid.
    
    This uses custom thresholds more suitable for a 3D neighborhood of 26 neighbors:
      - A live cell stays alive if it has 9 to 17 neighbors (inclusive).
      - A dead cell becomes alive if it has 10 to 15 neighbors (inclusive).
    
    Feel free to tweak these values for different 3D automaton behaviors.
    """
    # Adjust these as you wish:
    survival_min, survival_max = 9, 17
    birth_min, birth_max = 10, 15
    
    nx, ny, nz = grid.shape
    new_grid = np.zeros((nx, ny, nz), dtype=int)
    
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                neighbors = count_neighbors_3d(grid, x, y, z)
                
                if grid[x, y, z] == 1:
                    # Survival condition
                    if survival_min <= neighbors <= survival_max:
                        new_grid[x, y, z] = 1
                else:
                    # Birth condition
                    if birth_min <= neighbors <= birth_max:
                        new_grid[x, y, z] = 1
                        
    return new_grid

def main():
    global window_open
    
    # Larger grid for more space (feel free to adjust):
    nx, ny, nz = 20, 20, 20
    
    # Random initialization: 80% dead, 20% alive (adjust for sparser/denser starts)
    grid = np.random.choice([0, 1], size=(nx, ny, nz), p=[0.8, 0.2])
    
    generations = 100  # Simulate more generations
    
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
        
        # Find coordinates of living cells
        living_cells = np.argwhere(grid == 1)
        
        if living_cells.size > 0:
            xs, ys, zs = living_cells[:, 0], living_cells[:, 1], living_cells[:, 2]
            ax.scatter(xs, ys, zs, marker='o')
        
        ax.set_xlim(0, nx)
        ax.set_ylim(0, ny)
        ax.set_zlim(0, nz)
        ax.set_title(f"3D Game of Life (Toroidal) - Generation {gen}")
        
        plt.draw()
        
        # Pause so we can see the update
        try:
            plt.pause(0.2)
        except:
            # If pause fails (e.g., window closed mid-pause), exit the loop
            break
        
        # Move to the next generation
        grid = next_generation_3d(grid)

    # Shut down cleanly
    plt.ioff()
    plt.close(fig)
    sys.exit()

if __name__ == "__main__":
    main()
