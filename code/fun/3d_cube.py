from ursina import *

app = Ursina()

# Set the background color to black
window.color = color.black

# Function to create a small cube
def create_small_cube(position, size):
    return Entity(model='cube', position=position, scale=(size, size, size), color=color.cyan, parent=pivot)

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

# Create a pivot entity to rotate the large cube
pivot = Entity()

# Create a large cube composed of smaller cubes
large_cube_size = 5
num_cubes = 3
create_large_cube(size=large_cube_size, num_cubes=num_cubes)

# Function to update the rotation of the large cube
def update():
    pivot.rotation_x += 0.2  # Slowly rotate around the X-axis

# Set the camera position and rotation to fit the cube in the window
camera.position = (50, 50, 50)
camera.look_at(pivot)

app.run()
