import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import convolve2d

def update(frameNum, img, grid, kernel):
    neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')
    newGrid = ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | ((grid == 0) & (neighbors == 3))
    img.set_data(newGrid)
    grid[:] = newGrid
    return img,

def main():
    N = 100
    grid = np.random.choice([1, 0], size=(N, N), p=[0.2, 0.8])
    
    # Kernel to count neighbors
    kernel = np.array([[1,1,1], [1,0,1], [1,1,1]])

    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest', cmap='binary')
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, kernel), interval=30)

    plt.show()

if __name__ == '__main__':
    main()
