from ursina import *

app = Ursina()

# Get the directory of the currently running script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct full paths to the shader files
vertex_shader_path = os.path.join(script_dir, "color_shader.vert")
fragment_shader_path = os.path.join(script_dir, "color_shader.frag")

# Load custom shader
shader = Shader(
    language=Shader.GLSL,
    vertex=open(vertex_shader_path, "r").read(),
    fragment=open(fragment_shader_path, "r").read()
)

# Create a cube entity
cube = Entity(
    model='cube',
    shader=shader,  # Apply the shader here
    scale=2,
    collider='box'
)

instructions = Text(
    text="Use arrows to move, click to rotate, and mouse scroll to zoom",
    origin=(0, 0),  # Center the text
    position=(0, -.45),  # Adjust position so it doesn’t overlap with the cube
    background=True,  # Optional: make it stand out with a background
    scale=2
)

# This function rotates the cube by 360 degrees when called
def rotate_cube():
    cube.animate('rotation_y', cube.rotation_y + 360, duration=2, curve=curve.in_out_expo)
    invoke(reset_cube_position, delay=2)

# This function resets the cube's position
def reset_cube_position():
    cube.rotation_y = 0

def update():
    # Move the cube left and right based on arrow key input
    if held_keys['right arrow']:
        cube.x += 5 * time.dt
    elif held_keys['left arrow']:
        cube.x -= 5 * time.dt
    elif held_keys['up arrow']:
        cube.y += 5 * time.dt
    elif held_keys['down arrow']:
        cube.y -= 5 * time.dt

cube.on_click = rotate_cube

# Add camera controls to orbit and move the camera
EditorCamera()

app.run()
