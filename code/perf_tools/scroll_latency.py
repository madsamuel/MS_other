import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import random

# Define latency values for each text box in milliseconds
latencies = [0, 100, 200, 300, 400, 500, 600]

# Shuffle the latency array to randomize assignments
random.shuffle(latencies)

# Initialize an empty response dictionary
responses = {}

# Load lorem ipsum text from file
with open("lorem_ipsum.txt", "r") as file:
    lorem_text = file.read()

def handle_scroll(event, textbox, total_latency_ms):    
    current_time = time.time()
    if not hasattr(textbox, 'last_scroll_time'):
        textbox.last_scroll_time = 0
    if current_time - textbox.last_scroll_time > total_latency_ms / 1000:
        textbox.yview_scroll(-1 * (event.delta // 120), "units")
        textbox.last_scroll_time = current_time
    return "break"

# Function to handle the report button click
def handle_report(latency_ms, box_name):
    response = messagebox.askyesno(
        "Scrolling Latency Test", f"Did you notice a delay in {box_name} between scrolling with the mouse and responsivness?"
    )
    response_text = "Yes" if response else "No"
    responses[box_name] = (latency_ms, response_text)

    # Print the response
    print(f"{box_name}: {response_text} (Assigned Latency: {latency_ms} ms)")

    # Save responses when all reports are done
    if len(responses) == len(latencies):
        with open("scroll_latency.log", "a") as file:
            log_entry = ",".join(
                [f"{box}-{latency}ms:{response}" for box, (latency, response) in responses.items()]
            )
            file.write(log_entry + "\n")
        print("Responses saved to scroll_latency.log")

# Create the main window
root = tk.Tk()
root.title("Scrolling Latency Test")

# Set the window icon
icon_path = "icon.ico"  
try:
    root.iconbitmap(icon_path)  # For Windows (.ico)
except tk.TclError:
    # For cross-platform support using .png
    from PIL import Image, ImageTk
    icon_image = ImageTk.PhotoImage(Image.open("icon.png"))
    root.wm_iconphoto(True, icon_image)

# Create a grid layout for text areas and buttons
rows = 2
cols = (len(latencies) + 1) // 2  # Split into two rows

for i, latency in enumerate(latencies):
    row = i // cols
    col = i % cols

    # Create a frame for each text box and button
    frame = tk.Frame(root)
    frame.grid(row=row, column=col, padx=10, pady=10)

    # Add a scrolled text box
    textbox = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 10))
    textbox.insert(tk.END, lorem_text)
    textbox.config(state=tk.DISABLED)  # Disable editing
    textbox.pack()

    # Bind mouse scroll event with delay logic
    textbox.bind("<MouseWheel>", lambda e, tb=textbox, lat=latency: handle_scroll(e, tb, lat))

    # Add a report button below each text box
    button = tk.Button(
        frame,
        text="Report",
        command=lambda l=latency, bn=f"Text Box {i + 1}": handle_report(l, bn),
    )
    button.pack(pady=5)

# Run the GUI event loop
root.mainloop()
