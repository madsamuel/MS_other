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

# Add movement functionality for Mario
mario_position = [0, 0]  # Initial position of Mario

def move_left():
    mario_position[0] -= WALK_SPEED
    update_mario_position()

def move_right():
    mario_position[0] += WALK_SPEED
    update_mario_position()

def update_mario_position():
    turtle.clear()  # Clear the screen
    draw_mario_at_position(mario_position)

def draw_mario_at_position(position):
    turtle.speed(0)
    turtle.hideturtle()
    turtle.penup()
    turtle.tracer(0, 0)
    for y, row in enumerate(mario_pixels):
        for x, color in enumerate(row):
            if color:
                turtle.goto(position[0] + x * PIXEL_SIZE - WIDTH // 2, position[1] + HEIGHT // 2 - y * PIXEL_SIZE)
                turtle.fillcolor(color)
                turtle.begin_fill()
                for _ in range(4):
                    turtle.forward(PIXEL_SIZE)
                    turtle.right(90)
                turtle.end_fill()
    turtle.update()

# Modify movement to support holding keys
def move_left_continuous():
    mario_position[0] -= WALK_SPEED
    update_mario_position()
    turtle.ontimer(move_left_continuous, 50)  # Repeat every 50ms

def move_right_continuous():
    mario_position[0] += WALK_SPEED
    update_mario_position()
    turtle.ontimer(move_right_continuous, 50)  # Repeat every 50ms

def stop_movement():
    turtle.ontimer(None, 0)  # Stop the continuous movement

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
    screen.listen()
    screen.onkeypress(move_left_continuous, "Left")
    screen.onkeypress(move_right_continuous, "Right")
    screen.onkeyrelease(stop_movement, "Left")
    screen.onkeyrelease(stop_movement, "Right")
    draw_mario_at_position(mario_position)
    screen.mainloop()

if __name__ == "__main__":
    main()