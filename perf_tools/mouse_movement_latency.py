import tkinter as tk
import random
import time

# Define latency values for each canvas in milliseconds
latencies = [0, 10, 20, 30, 40, 50, 60]

# Shuffle latencies to randomize their assignment to canvases
random.shuffle(latencies)

# Store canvas references for clearing
canvases = []

def handle_draw(event, canvas, latency_ms):
    """
    Simulate latency in drawing by delaying the drawing action.
    :param event: The mouse event.
    :param canvas: The canvas on which to draw.
    :param latency_ms: The latency in milliseconds.
    """
    x, y = event.x, event.y  # Get the current cursor position

    # Introduce latency before drawing
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time) < (latency_ms / 1000.0):
        pass

    # Draw a small oval to simulate drawing with the delayed cursor
    canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="black")

def clear_canvases():
    """Clear all canvases."""
    for canvas in canvases:
        canvas.delete("all")

# Create the main window
root = tk.Tk()
root.title("Mouse Latency Drawing Test")

# Set the window icon
icon_path = "my_icon.ico"  # Change to your icon file's path
try:
    root.iconbitmap(icon_path)  # For Windows (.ico)
except tk.TclError:
    # For cross-platform support using .png
    from PIL import Image, ImageTk
    icon_image = ImageTk.PhotoImage(Image.open("my_icon.png"))
    root.wm_iconphoto(True, icon_image)

# Create a frame for the canvases
canvas_frame = tk.Frame(root)
canvas_frame.pack()

# Create a grid layout for canvases
rows = 2
cols = (len(latencies) + 1) // 2  # Split into two rows

for i, latency in enumerate(latencies):
    row = i // cols
    col = i % cols

    # Create a frame for each canvas
    frame = tk.Frame(canvas_frame, padx=10, pady=10)
    frame.grid(row=row, column=col)

    # Add a label above each canvas
    label = tk.Label(frame, text=f"Canvas {i + 1} (Latency: {latency} ms)")
    label.pack()

    # Add a canvas for drawing
    canvas = tk.Canvas(frame, width=300, height=200, bg="white")
    canvas.pack()
    canvases.append(canvas)  # Store the canvas reference for clearing

    # Bind the mouse motion event to simulate delayed drawing
    canvas.bind(
        "<Motion>",
        lambda event, c=canvas, l=latency: handle_draw(event, c, l)
    )

# Add a "Clear All" button below the canvases
clear_button = tk.Button(root, text="Clear All", command=clear_canvases)
clear_button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
