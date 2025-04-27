from ursina import *

app = Ursina()

cube = Entity(
    model='cube',
    scale=(2, 2, 2)
)

# Access the mesh of the cube and set colors
vertex_colors = [
    color.rgb(0, 0, 0),      # Black
    color.rgb(255, 0, 0),    # Red
    color.rgb(0, 255, 0),    # Green
    color.rgb(0, 0, 255),    # Blue
    color.rgb(255, 255, 0),  # Yellow
    color.rgb(255, 0, 255),  # Magenta
    color.rgb(0, 255, 255),  # Cyan
    color.rgb(255, 255, 255) # White
]

cube.model.vertex_colors = vertex_colors
cube.model.generate()

EditorCamera()  # Allows rotation with mouse

app.run()
