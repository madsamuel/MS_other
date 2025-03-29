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

    # Set up figure with two axes: one for grid, one for text
    fig, (ax_grid, ax_text) = plt.subplots(2, 1, figsize=(6, 6.5),
                                           gridspec_kw={'height_ratios': [20, 1]})

    # Game grid
    img = ax_grid.imshow(grid, interpolation='nearest', cmap='binary')
    ax_grid.axis('off')

    # Generation label (in separate axis)
    ax_text.axis('off')
    gen_text = ax_text.text(0.5, 0.5, 'Generation: 0', ha='center', va='center',
                            fontsize=12, color='black')

    ani = animation.FuncAnimation(fig, update,
                                  fargs=(img, grid, kernel, gen_text),
                                  interval=30)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
