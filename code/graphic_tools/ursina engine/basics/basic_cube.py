from ursina import *

app = Ursina()

# Create a cube entity
cube = Entity(
    model='cube',
    color=hsv(300, 1, 1),  # Pinkish hue
    scale=2,
    collider='box'
)

# This function rotates the cube by 360 degrees when called
def rotate_cube():
    # Animate the cube’s rotation, then reset position after the spin
    cube.animate('rotation_y', cube.rotation_y + 360, duration=2, curve=curve.in_out_expo)
    invoke(reset_cube_position, delay=2)

# This function resets the cube's position
def reset_cube_position():
    cube.rotation_y = 0

# Assign the on-click function
cube.on_click = rotate_cube

# Add camera controls to orbit and move the camera
EditorCamera()

# Run the Ursina application
app.run()
