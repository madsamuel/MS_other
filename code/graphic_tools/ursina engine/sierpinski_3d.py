from ursina import *

def sierpinski_tetrahedron(order, size=1, position=(0,0,0)):
    """
    Recursively spawn a Sierpinski Tetrahedron of a given 'order' and 'size'
    at the given 'position' (x, y, z).

    If order = 0, we just create a single tetrahedron.
    Otherwise, we subdivide into 4 smaller tetrahedrons.
    """
    if order == 0:
        # Base case: spawn a single tetrahedron
        Entity(
            model='tetra',
            position=position,
            scale=size,
            color=color.random_color()  # random colors for fun
        )
    else:
        # Subdivide
        offset = size / 2
        x, y, z = position

        # 1) Top
        sierpinski_tetrahedron(
            order-1, offset,
            (x,       y + offset, z     )
        )
        # 2) Bottom-left-back
        sierpinski_tetrahedron(
            order-1, offset,
            (x - offset, y - offset, z - offset)
        )
        # 3) Bottom-right-back
        sierpinski_tetrahedron(
            order-1, offset,
            (x + offset, y - offset, z - offset)
        )
        # 4) Bottom-center-front
        sierpinski_tetrahedron(
            order-1, offset,
            (x, y - offset, z + offset)
        )

def main():
    # Initialize Ursina
    app = Ursina()

    # Position the camera
    camera.position = (0, 25, -60)
    camera.look_at((0, 0, 0))

    # Optionally add a directional light for shading
    DirectionalLight(
        parent=scene,
        rotation=(45, 45, 45),
        shadows=True
    )

    # Create the Sierpinski Tetrahedron fractal
    # Increase "order" for more detail, "size" for overall scale
    sierpinski_tetrahedron(order=3, size=15, position=(0, 0, 0))

    # Start the Ursina engine
    app.run()

if __name__ == '__main__':
    main()
