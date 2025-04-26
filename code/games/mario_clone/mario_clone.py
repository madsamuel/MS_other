import turtle

# Game constants
WIDTH, HEIGHT = 640, 480
PIXEL_SIZE = 8
GRAVITY = 0.6
JUMP_STRENGTH = -12
RUN_SPEED = 8
WALK_SPEED = 4

# Colors
BLACK = "black"
RED = "red"
BLUE = "blue"
BROWN = "#8B4513"
SKIN = "#FFE0BD"
YELLOW = "yellow"
CLEAR = None

# Simplified Mario Pixel Art (16x16 based on provided image)
mario_pixels = [
    [CLEAR, CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, BROWN, BROWN, BROWN, SKIN, SKIN, BLACK, SKIN, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, SKIN, BROWN, SKIN, SKIN, SKIN, BLACK, SKIN, SKIN, SKIN, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, SKIN, BROWN, BROWN, SKIN, SKIN, SKIN, BLACK, SKIN, SKIN, SKIN, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, BROWN, SKIN, SKIN, SKIN, SKIN, BLACK, BLACK, BLACK, BLACK, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, CLEAR, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, RED, RED, BLUE, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, RED, RED, RED, BLUE, RED, RED, BLUE, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, RED, RED, RED, BLUE, BLUE, BLUE, BLUE, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, RED, RED, BLUE, YELLOW, BLUE, BLUE, YELLOW, BLUE, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, CLEAR, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, CLEAR, RED, RED, RED, RED, RED, RED, RED, RED, RED, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, CLEAR, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR, CLEAR, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR, CLEAR],
    [CLEAR, BROWN, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR, CLEAR, BROWN, BROWN, BROWN, BROWN, CLEAR, CLEAR, CLEAR],
]

# Draw Mario using turtle
def draw_mario():
    turtle.speed(0)  # Set the fastest drawing speed
    turtle.hideturtle()
    turtle.penup()
    turtle.tracer(0, 0)  # Disable screen updates for faster drawing
    for y, row in enumerate(mario_pixels):
        for x, color in enumerate(row):
            if color:
                turtle.goto(x * PIXEL_SIZE - WIDTH // 2, HEIGHT // 2 - y * PIXEL_SIZE)
                turtle.fillcolor(color)
                turtle.begin_fill()
                for _ in range(4):
                    turtle.forward(PIXEL_SIZE)
                    turtle.right(90)
                turtle.end_fill()
    turtle.update()  # Update the screen after all drawing is done

# Setup turtle screen
def setup_screen():
    screen = turtle.Screen()
    screen.setup(WIDTH, HEIGHT)
    screen.bgcolor("#6A96FC")
    screen.title("Mario Pixel Art Clone")
    return screen

# Main game loop
def main():
    screen = setup_screen()
    draw_mario()
    screen.mainloop()

if __name__ == "__main__":
    main()