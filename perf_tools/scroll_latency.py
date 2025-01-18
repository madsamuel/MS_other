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
    steps = int(-1 * (event.delta / 120))  # Calculate scroll steps
    if steps == 0:
        return 

    # Calculate latency per step
    latency_per_step = total_latency_ms / abs(steps) if abs(steps) > 0 else total_latency_ms

    for _ in range(abs(steps)):
        # Perform one scroll step
        textbox.yview_scroll(1 if steps > 0 else -1, "units")

        # Simulate latency for this step
        start_time = time.perf_counter()
        while (time.perf_counter() - start_time) < (latency_per_step / 1000.0):
            pass

    return 


# Function to handle the report button click
def handle_report(latency_ms, box_name):
    response = messagebox.askyesno(
        "Scrolling Latency Test", f"Did you notice a delay in {box_name}?"
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

    # Bind the scrolling event to introduce latency
    textbox.bind(
        "<MouseWheel>",
        lambda event, tb=textbox, l=latency: handle_scroll(event, tb, l),
    )

    # Add a report button below each text box
    button = tk.Button(
        frame,
        text="Report",
        command=lambda l=latency, bn=f"Text Box {i + 1}": handle_report(l, bn),
    )
    button.pack(pady=5)

# Run the GUI event loop
root.mainloop()
