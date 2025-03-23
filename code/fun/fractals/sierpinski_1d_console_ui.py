import turtle

def sierpinski_triangle(t, order, length):
    """
    Draw a Sierpinski Triangle of a given 'order' and 'length' using the turtle 't'.
    If order = 0, simply draw an equilateral triangle.
    Otherwise, subdivide into 3 smaller Sierpinski triangles of order-1.
    """

    if order == 0:
        # Draw an equilateral triangle
        for _ in range(3):
            t.forward(length)
            t.left(120)
    else:
        # 1. Draw top smaller triangle
        sierpinski_triangle(t, order - 1, length / 2)

        # 2. Move turtle forward
        t.forward(length / 2)
        # 3. Draw bottom-right smaller triangle
        sierpinski_triangle(t, order - 1, length / 2)

        # 4. Move turtle back
        t.backward(length / 2)

        # 5. Tilt left 60°, move forward length/2, tilt right 60° for bottom-left
        t.left(60)
        t.forward(length / 2)
        t.right(60)

        # 6. Draw the bottom-left smaller triangle
        sierpinski_triangle(t, order - 1, length / 2)

        # 7. Move turtle back to original position
        t.left(60)
        t.backward(length / 2)
        t.right(60)

def main():
    # 1. Setup the screen
    screen = turtle.Screen()
    screen.title("Sierpinski Triangle")
    screen.setup(width=800, height=600)

    # 2. Create a turtle
    t = turtle.Turtle()
    t.speed("fastest")
    t.penup()
    # Position turtle so triangle is centered (adjust as desired)
    t.goto(-200, -150)
    t.pendown()

    # 3. Draw the Sierpinski Triangle
    # You can experiment with different orders (2, 3, 4, etc.)
    order = 4
    length = 400

    sierpinski_triangle(t, order, length)

    # 4. Keep the window open until closed by the user
    turtle.done()

if __name__ == "__main__":
    main()
