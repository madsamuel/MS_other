import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def mandelbox_point_cloud(scale, iterations, resolution, threshold):
    points = []
    for x in np.linspace(-1.5, 1.5, resolution):
        for y in np.linspace(-1.5, 1.5, resolution):
            for z in np.linspace(-1.5, 1.5, resolution):
                c = np.array([x, y, z])
                distance = mandelbox_distance_estimator(c, scale, iterations)
                if distance < threshold:
                    points.append(c)
    return np.array(points)

# Parameters
scale = 2.0
iterations = 10
resolution = 50
threshold = 0.01

# Generate point cloud
points = mandelbox_point_cloud(scale, iterations, resolution, threshold)

# Plotting
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(points[:, 0], points[:, 1], points[:, 2], color='blue', s=0.1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()
