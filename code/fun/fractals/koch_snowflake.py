import turtle

def koch_curve(t, order, length):
    """
    Draw a Koch curve with a given 'order' and 'length' using the turtle 't'.
    """
    if order == 0:
        t.forward(length)
    else:
        length /= 3.0
        # 1. Draw a Koch curve of order-1
        koch_curve(t, order - 1, length)
        # 2. Turn left 60°
        t.left(60)
        # 3. Another Koch curve of order-1
        koch_curve(t, order - 1, length)
        # 4. Turn right 120°
        t.right(120)
        # 5. Another Koch curve of order-1
        koch_curve(t, order - 1, length)
        # 6. Turn left 60° again
        t.left(60)
        # 7. Last Koch curve of order-1
        koch_curve(t, order - 1, length)

def koch_snowflake(t, order, length):
    """
    Draw a complete Koch snowflake (3 Koch curves in a triangle).
    """
    for _ in range(3):
        koch_curve(t, order, length)
        t.right(120)

def main():
    # Create a turtle screen and turtle instance
    screen = turtle.Screen()
    screen.title("Koch Snowflake")
    screen.setup(width=800, height=600)
    
    t = turtle.Turtle()
    t.speed("fastest")
    t.penup()
    # Position the turtle so the snowflake is centered
    t.goto(-200, 100)
    t.pendown()

    # Draw a Koch snowflake of order 3 with side length 400
    order = 3
    side_length = 400

    koch_snowflake(t, order, side_length)

    # Keep the window open until closed by the user
    turtle.done()

if __name__ == "__main__":
    main()
