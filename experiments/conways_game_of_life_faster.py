import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import convolve2d

def update(frameNum, img, grid, kernel, gen_text):
    neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')
    newGrid = ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | ((grid == 0) & (neighbors == 3))
    img.set_data(newGrid)
    grid[:] = newGrid
    gen_text.set_text(f'Generation: {frameNum}')
    return img, gen_text

def main():
    N = 100
    grid = np.random.choice([1, 0], size=(N, N), p=[0.2, 0.8])
    kernel = np.array([[1,1,1], [1,0,1], [1,1,1]])

    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest', cmap='binary')
    ax.axis('off')  # Hide axes

    # Add generation text
    gen_text = ax.text(0.02, 0.95, 'Generation: 0', color='lime',
                       fontsize=12, transform=ax.transAxes, ha='left', va='top',
                       bbox=dict(facecolor='black', alpha=0.5, boxstyle='round'))

    ani = animation.FuncAnimation(fig, update,
                                  fargs=(img, grid, kernel, gen_text),
                                  interval=30)
    plt.show()

if __name__ == '__main__':
    main()
