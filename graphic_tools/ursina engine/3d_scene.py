from ursina import *

# Helper metallic-like shader
class MetallicMaterial(Shader):
    def __init__(self, color=color.rgb(0,112,243), alpha=0.9):
        super().__init__(
            fragment='''
#version 150
uniform vec4 p3d_ColorScale;
in vec2 uv;
in vec4 color;
in vec3 normal;
in vec3 world_normal;
in vec3 world_position;
out vec4 fragColor;

void main() {
    // Basic directional lighting
    vec3 light_dir = normalize(vec3(0.5, 0.5, 0.5));
    float light_intensity = max(dot(normalize(world_normal), light_dir), 0.0);

    // base color from p3d_ColorScale
    vec3 base = p3d_ColorScale.rgb;
    // simple shading
    vec3 shaded = base * (0.2 + 0.8 * light_intensity);

    fragColor = vec4(shaded, p3d_ColorScale.a);
}
''',
        )
        self.default_input = {
            'p3d_ColorScale': Vec4(color.r, color.g, color.b, alpha)
        }

def create_box_with_edges(position=(0,0,0)):
    group = Entity(position=position)

    # The main fill cube (the 'metallic' or normal material)
    fill = Entity(
        parent=group,
        model='cube',
        color=color.azure,   # or some custom color
        scale=(0.5, 0.5, 0.5)
    )

    # A wireframe overlay, slightly bigger than the fill
    outline = Entity(
        parent=group,
        model='cube',
        wireframe=True,
        color=color.white,   # or any line color
        scale=(0.51, 0.51, 0.51)
    )

    return group


def get_letter_shape(letter):
    shapes = {
        'N': [
            [1,0,0,0,1],
            [1,1,0,0,1],
            [1,0,1,0,1],
            [1,0,0,1,1],
            [1,0,0,0,1],
        ],
        'E': [
            [1,1,1],
            [1,0,0],
            [1,1,0],
            [1,0,0],
            [1,1,1],
        ],
        'X': [
            [1,0,0,0,1],
            [0,1,0,1,0],
            [0,0,1,0,0],
            [0,1,0,1,0],
            [1,0,0,0,1],
        ],
        'T': [
            [1,1,1],
            [0,1,0],
            [0,1,0],
            [0,1,0],
            [0,1,0],
        ],
    }
    return shapes.get(letter, shapes['N'])  # default to 'N'

def create_letter(letter='N', position=(0,0,0)):
    group = Entity(position=position)
    shape = get_letter_shape(letter)

    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                xOffset = j*0.5
                if letter == 'T':
                    xOffset -= 1
                elif letter == 'E':
                    xOffset -= 0.5
                elif letter in ('X', 'N'):
                    xOffset -= 1

                if letter == 'N':
                    if j == 0: xOffset = -0.5
                    elif j == 1: xOffset = 0
                    elif j == 2: xOffset = 0.25
                    elif j == 3: xOffset = 0.5
                    elif j == 4: xOffset = 1

                if letter == 'X':
                    if j == 0: xOffset = -1
                    elif j == 1: xOffset = -0.75
                    elif j == 2: xOffset = -0.25
                    elif j == 3: xOffset = 0.25
                    elif j == 4: xOffset = 0.5

                yOffset = (4 - i)*0.5 - 1
                create_box_with_edges(position=(xOffset, yOffset, 0)).parent = group

    return group

def update():
    global main_group
    main_group.rotation_y += time.dt * 30  # auto-rotate letters group

def init_scene():
    g = Entity(position=(-0.5, 0, 0), rotation=(0, 90, 0))
    create_letter('N', position=(-3.75, 0, 0)).parent = g
    create_letter('E', position=(-1.25, 0, 0)).parent = g
    create_letter('X', position=(1.25, 0, 0)).parent = g
    create_letter('T', position=(3.75, 0, 0)).parent = g
    return g

def main():
    app = Ursina()

    window.color = color.black  # simple background color

    # Use EditorCamera for orbit/zoom/pan
    cam = EditorCamera(rotation=(0, 0, 0), fov=50)
    cam.y = 0

    global main_group
    main_group = init_scene()

    # A bit of lighting
    directional_light = DirectionalLight(color=color.white, shadows=True)
    directional_light.look_at((1, 1, 1))
    ambient_light = AmbientLight(color=color.rgba(255,255,255,128))

    app.run()

if __name__ == '__main__':
    main()
