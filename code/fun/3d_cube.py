from ursina import *

app = Ursina()

# Function to create a small cube
def create_small_cube(position, size):
    return Entity(model='cube', position=position, scale=size, color=color.cyan)

# Function to create a large cube composed of smaller cubes
def create_large_cube(size, num_cubes):
    small_cube_size = size / num_cubes
    for i in range(num_cubes):
        for j in range(num_cubes):
            for k in range(num_cubes):
                position = (i * small_cube_size - size/2 + small_cube_size/2,
                            j * small_cube_size - size/2 + small_cube_size/2,
                            k * small_cube_size - size/2 + small_cube_size/2)
                create_small_cube(position, small_cube_size)

# Create a large cube composed of smaller cubes
create_large_cube(size=10, num_cubes=3)

# Create a pivot entity to rotate the large cube
pivot = Entity()

# Function to update the rotation of the large cube
def update():
    pivot.rotation_y += 1  # Rotate around the Y-axis
    pivot.rotation_x += 1  # Rotate around the X-axis

EditorCamera()

app.run()
