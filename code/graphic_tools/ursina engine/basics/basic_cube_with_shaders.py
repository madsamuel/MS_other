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

# This function rotates the cube by 360 degrees when called
def rotate_cube():
    cube.animate('rotation_y', cube.rotation_y + 360, duration=2, curve=curve.in_out_expo)
    invoke(reset_cube_position, delay=2)

# This function resets the cube's position
def reset_cube_position():
    cube.rotation_y = 0

cube.on_click = rotate_cube

# Add camera controls to orbit and move the camera
EditorCamera()

app.run()
