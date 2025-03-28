import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def update(frameNum, img, grid, N):
    # copy grid since we require 8 neighbors for calculation
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            # compute 8-neighbor sum using toroidal boundary conditions
            total = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] +
                         grid[(i-1)%N, j] + grid[(i+1)%N, j] +
                         grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
                         grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N]))
            # apply Conway's rules
            if grid[i, j]  == 1:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = 0
            else:
                if total == 3:
                    newGrid[i, j] = 1
    # update data
    img.set_data(newGrid)
    grid[:] = newGrid[:]
    return img,

# main function
def main():
    # set grid size
    N = 500
    # set animation update interval
    updateInterval = 50
    # declare grid
    grid = np.array([])

    # populate grid with random on/off - more off than on
    grid = np.random.choice([1,0], N*N, p=[0.3, 0.7]).reshape(N, N)

    # set up animation
    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N, ),
                                  frames=10,
                                  interval=updateInterval,
                                  save_count=50)

    plt.show()

# call main
if __name__ == '__main__':
    main()
