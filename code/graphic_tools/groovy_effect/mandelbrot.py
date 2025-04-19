import numpy as np
import matplotlib.pyplot as plt

# Image size (pixels)
width, height = 800, 800
zoom = 1.5

# Coordinate ranges
x = np.linspace(-2.5, 1.5, width)
y = np.linspace(-2.0, 2.0, height)
X, Y = np.meshgrid(x, y)
C = X + 1j * Y

Z = np.zeros_like(C)
mandelbrot_set = np.zeros(C.shape, dtype=int)

max_iter = 100

for i in range(max_iter):
    mask = np.abs(Z) <= 2
    Z[mask] = Z[mask] ** 2 + C[mask]
    mandelbrot_set[mask] = i

plt.figure(figsize=(10, 10))
plt.imshow(mandelbrot_set, cmap='inferno', extent=(-2.5, 1.5, -2, 2))
plt.axis('off')
plt.title('Mandelbrot Set')
plt.show()
