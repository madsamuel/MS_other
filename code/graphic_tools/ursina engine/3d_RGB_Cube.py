from ursina import *

app = Ursina()

# Set the background color to black
window.color = color.black

rgb_cube = Entity()  # Parent entity for all small cubes

resolution = 8  # How many subdivisions along each axis
size = 2         # Overall cube size
half = size / 2

for x in range(resolution):
    for y in range(resolution):
        for z in range(resolution):
            # Correct color mapping: x -> R, y -> G, z -> B
            r = int((x / (resolution - 1)) * 255)
            g = int((y / (resolution - 1)) * 255)
            b = int((z / (resolution - 1)) * 255)

            Entity(
                parent=rgb_cube,
                model=Mesh(vertices=[
                    Vec3(-0.5, -0.5, -0.5), Vec3(0.5, -0.5, -0.5), Vec3(0.5, 0.5, -0.5), Vec3(-0.5, 0.5, -0.5),
                    Vec3(-0.5, -0.5, 0.5), Vec3(0.5, -0.5, 0.5), Vec3(0.5, 0.5, 0.5), Vec3(-0.5, 0.5, 0.5)
                ],
                triangles=[
                    (0,1,2), (0,2,3), (1,5,6), (1,6,2),
                    (5,4,7), (5,7,6), (4,0,3), (4,3,7),
                    (3,2,6), (3,6,7), (4,5,1), (4,1,0)
                ],
                colors=[
                    color.rgba(r, g, b, 200)]*8,  # More solid (brighter)
                mode='triangle'),
                position=Vec3(
                    lerp(-half, half, x / (resolution - 1)),
                    lerp(-half, half, y / (resolution - 1)),
                    lerp(-half, half, z / (resolution - 1))
                ),
                scale=size / resolution * 0.9
            )

EditorCamera()

# Rotate the whole RGB cube slowly
def update():
    rgb_cube.rotation_y += time.dt * 20  # 20 degrees per second

app.run()
