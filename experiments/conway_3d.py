import numpy as np
import matplotlib.pyplot as plt
import time

def count_neighbors_3d(grid, x, y, z):
    """
    Count the number of alive neighbors around cell (x, y, z) in the 3D grid.
    Neighbors are all surrounding cells within 1 step in each dimension,
    excluding the cell itself (26 neighbors total in 3D).
    """
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
                
                # Check boundaries
                if 0 <= nx_pos < nx and 0 <= ny_pos < ny and 0 <= nz_pos < nz:
                    count += grid[nx_pos, ny_pos, nz_pos]
                    
    return count

def next_generation_3d(grid):
    """
    Compute the next generation of the 3D Game of Life based on the current grid.
    Using standard Conway-like rules adapted to 3D:
      - A live cell stays alive if it has 2 or 3 neighbors.
      - A dead cell becomes alive if it has exactly 3 neighbors.
    """
    nx, ny, nz = grid.shape
    new_grid = np.zeros((nx, ny, nz), dtype=int)
    
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                alive_neighbors = count_neighbors_3d(grid, x, y, z)
                
                if grid[x, y, z] == 1:
                    # Survival rule
                    if alive_neighbors == 2 or alive_neighbors == 3:
                        new_grid[x, y, z] = 1
                else:
                    # Birth rule
                    if alive_neighbors == 3:
                        new_grid[x, y, z] = 1
                        
    return new_grid

def main():
    # Grid size (small to keep it manageable)
    nx, ny, nz = 8, 8, 8

    # Random initialization: 50% chance alive, 50% dead
    grid = np.random.choice([0, 1], size=(nx, ny, nz), p=[0.5, 0.5])
    
    # Number of generations to simulate
    generations = 30
    
    # Set up interactive plotting
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    for gen in range(generations):
        ax.clear()
        
        # Extract coordinates of all living cells
        living_cells = np.argwhere(grid == 1)
        
        if living_cells.size > 0:
            xs, ys, zs = living_cells[:, 0], living_cells[:, 1], living_cells[:, 2]
            ax.scatter(xs, ys, zs, marker='o')
        
        # Set the plot boundaries
        ax.set_xlim(0, nx)
        ax.set_ylim(0, ny)
        ax.set_zlim(0, nz)
        
        ax.set_title(f"3D Game of Life - Generation {gen}")
        plt.draw()
        plt.pause(0.5)  # pause so we can see the update

        # Advance to next generation
        grid = next_generation_3d(grid)

    # Keep the final plot open after the simulation
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    main()
