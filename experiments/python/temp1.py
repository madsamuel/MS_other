import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # needed for 3D plotting

# Define the function
def f(x, y):
    return 6 - 3*x - 2*y

# Create a grid of (x, y) values
x = np.linspace(-1, 3, 50)   # adjust range as you like
y = np.linspace(-1, 4, 50)
X, Y = np.meshgrid(x, y)
Z = f(X, Y)

# -------- 3D surface plot --------
fig = plt.figure(figsize=(10, 4))

ax1 = fig.add_subplot(1, 2, 1, projection="3d")
ax1.plot_surface(X, Y, Z, alpha=0.8)
ax1.set_title("Surface: z = 6 - 3x - 2y")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_zlabel("z")

# -------- Contour (top-down) plot --------
ax2 = fig.add_subplot(1, 2, 2)
contours = ax2.contour(X, Y, Z, levels=10)
ax2.clabel(contours, inline=True, fontsize=8)
ax2.set_title("Level curves of f(x, y)")
ax2.set_xlabel("x")
ax2.set_ylabel("y")

plt.tight_layout()
plt.show()
