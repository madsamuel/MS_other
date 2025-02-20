from ursina import *

# We'll keep track of the current player's symbol and color in a dictionary
current_player = {
    'symbol': 'o',
    'color': color.azure
}

# Create a 3x3 matrix of buttons for the board. We'll fill it in setup_board().
board = [[None for _ in range(3)] for _ in range(3)]

def toggle_player():
    """
    Switch between 'o' and 'x' for the current player.
    """
    if current_player['symbol'] == 'o':
        current_player['symbol'] = 'x'
        current_player['color'] = color.orange
    else:
        current_player['symbol'] = 'o'
        current_player['color'] = color.azure

def on_click(button):
    """
    Called when a board cell is clicked.
    We set the button's text to the current player's symbol,
    change its color, disable collision so it can't be clicked again,
    and then check for a win. Finally, we switch the player.
    """
    button.text = current_player['symbol']
    button.color = current_player['color']
    button.collision = False

    check_for_victory()

    # Switch player
    toggle_player()

def check_for_victory():
    """
    Checks if the current player has won.
    If yes, shows a victory panel and stops the game.
    """
    symbol = current_player['symbol']

    # Check rows, columns, diagonals for a win
    has_won = (
        # Rows
        (board[0][0].text == symbol and board[0][1].text == symbol and board[0][2].text == symbol) or
        (board[1][0].text == symbol and board[1][1].text == symbol and board[1][2].text == symbol) or
        (board[2][0].text == symbol and board[2][1].text == symbol and board[2][2].text == symbol) or
        # Columns
        (board[0][0].text == symbol and board[1][0].text == symbol and board[2][0].text == symbol) or
        (board[0][1].text == symbol and board[1][1].text == symbol and board[2][1].text == symbol) or
        (board[0][2].text == symbol and board[1][2].text == symbol and board[2][2].text == symbol) or
        # Diagonals
        (board[0][0].text == symbol and board[1][1].text == symbol and board[2][2].text == symbol) or
        (board[0][2].text == symbol and board[1][1].text == symbol and board[2][0].text == symbol)
    )

    if has_won:
        print(f'Player "{symbol}" wins!')
        mouse.visible = True
        # Display a victory message on screen
        Panel(z=1, scale=10, model='quad', color=color.white66)
        t = Text(
            text=f'Player "{symbol}" has won!',
            scale=2,
            origin=(0,0),
            color=current_player['color']
        )
        # Disable further clicks on the board
        for row in board:
            for cell in row:
                cell.collision = False

def setup_board():
    """
    Create a 3x3 grid of Button entities in 3D space.
    We store each button in the global 'board' list.
    """
    # We'll space them out in X and Z so they look like a grid in 3D.
    start_x = -1
    start_z = 1
    for x in range(3):
        for z in range(3):
            # Button is a 3D entity by default in Ursina (with a box/cube model).
            b = Button(
                parent=scene,
                model='cube',
                color=color.light_gray,
                highlight_color=color.gray,  # color on hover
                position=(start_x + x, 0, start_z - z),
                scale=0.9   # slightly smaller so there's a gap
            )
            # Attach a click event so each button calls on_click with itself
            b.on_click = lambda btn=b: on_click(btn)
            board[x][z] = b

if __name__ == '__main__':
    # Initialize the Ursina engine
    app = Ursina()

    # Set up a 3D camera angle so we see the board from above and in front
    camera.position = (0, 16, -6)
    camera.look_at((0,0,0))

    # Optional: add some light so the board isn't dark
    DirectionalLight(parent=camera, x=0, y=1, z=-1, shadows=True)

    # Create the 3D tic-tac-toe board
    setup_board()

    # Hide the mouse until someone wins
    mouse.visible = False

    app.run()
