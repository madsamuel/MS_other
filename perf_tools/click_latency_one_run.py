import tkinter as tk
from tkinter import messagebox
import time

# Define latency values in milliseconds
latencies = [6000, 500, 400, 300, 200, 100, 0]

# Initialize an empty response dictionary
responses = {}

# Function to show popups without waiting for user responses
def show_popup(index, x_offset, y_offset):
    popup_number = f"Popup {index + 1}"

    # Create a new top-level window for each popup
    popup = tk.Toplevel(root)
    popup.title(popup_number)

    # Position the popup with an offset to achieve the tiled effect
    popup.geometry(f"300x100+{x_offset}+{y_offset}")

    # Add a label and Yes/No buttons
    label = tk.Label(popup, text=f"{popup_number}: Did you notice any delay?")
    label.pack(pady=10)

    def on_response(response):
        response_text = "yes" if response else "no"
        responses[popup_number] = response_text
        popup.destroy()

        # If all responses are collected, save them to the log file
        if len(responses) == len(latencies):
            with open("results.log", "a") as file:
                log_entry = ",".join([f"{popup}:{response}" for popup, response in responses.items()])
                file.write(log_entry + "\n")
            print("Responses saved to results.log")

    # Yes/No buttons
    yes_button = tk.Button(popup, text="Yes", command=lambda: on_response(True))
    no_button = tk.Button(popup, text="No", command=lambda: on_response(False))

    yes_button.pack(side="left", padx=20)
    no_button.pack(side="right", padx=20)

# Helper function to schedule popups with offsets
def schedule_popup(index, latency, x_offset, y_offset):
    root.after(latency, show_popup, index, x_offset, y_offset)

# Function to start the test
def start_test():
    x_offset = 100  # Initial X position
    y_offset = 100  # Initial Y position

    for index, latency in enumerate(latencies):
        schedule_popup(index, latency, x_offset + index * 150, y_offset + index * 150)

# Create the main window
root = tk.Tk()
root.title("Sequential Latency Test")

# Create the single button
button = tk.Button(root, text="Start Test", command=start_test)
button.pack(pady=20)

# Start the GUI event loop
root.mainloop()
