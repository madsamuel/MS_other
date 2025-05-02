from ursina import *

app = Ursina()

# Set the background color to black
window.color = color.black

# Function to interpolate between two colors
def lerp_color(color1, color2, t):
    return color.rgb(
        color1[0] + (color2[0] - color1[0]) * t,
        color1[1] + (color2[1] - color1[1]) * t,
        color1[2] + (color2[2] - color1[2]) * t
    )

# Function to create a small cube with a specific color
def create_small_cube(position, size, color):
    return Entity(model='cube', position=position, scale=(size, size, size), color=color, parent=pivot)

# Function to create a large cube composed of smaller cubes with gradient colors
def create_large_cube(size, num_cubes):
    small_cube_size = size / num_cubes
    for i in range(num_cubes):
        for j in range(num_cubes):
            for k in range(num_cubes):
                position = (i * small_cube_size - size/2 + small_cube_size/2,
                            j * small_cube_size - size/2 + small_cube_size/2,
                            k * small_cube_size - size/2 + small_cube_size/2)

                # Initialize color to white
                c = color.white

                # Determine the color based on the face
                if i == 0:
                    c = lerp_color(color.red, color.blue, j / num_cubes)
                elif i == num_cubes - 1:
                    c = lerp_color(color.green, color.yellow, j / num_cubes)
                elif j == 0:
                    c = lerp_color(color.blue, color.magenta, k / num_cubes)
                elif j == num_cubes - 1:
                    c = lerp_color(color.cyan, color.white, k / num_cubes)
                elif k == 0:
                    c = lerp_color(color.magenta, color.red, i / num_cubes)
                elif k == num_cubes - 1:
                    c = lerp_color(color.white, color.yellow, i / num_cubes)

                create_small_cube(position, small_cube_size, c)

# Create a pivot entity to rotate the large cube
pivot = Entity()

# Create a large cube composed of smaller cubes
large_cube_size = 5
num_cubes = 5
create_large_cube(size=large_cube_size, num_cubes=num_cubes)

# Function to update the rotation of the large cube
def update():
    pivot.rotation_x += 0.1  # Slowly rotate around the X-axis

# Set the camera position and rotation to fit the cube in the window
camera.position = (50, 50, 50)
camera.look_at(pivot)

app.run()
