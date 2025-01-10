import tkinter as tk
from tkinter import messagebox
import time

# Define latency values for each text box in milliseconds
latencies = [0, 100, 200, 300, 400, 500, 600]

# Initialize an empty response dictionary
responses = {}

# Function to handle text box submissions
def text_entry_submit(entry_name, latency_ms):
    start_time = time.perf_counter()  # Record the start time
    
    # Function to show the popup after the exact latency has passed
    def show_popup():
        end_time = time.perf_counter()  # Record the end time
        actual_latency = round((end_time - start_time) * 1000, 2)  # Calculate actual latency in ms

        # Show the popup asking for user feedback
        response = messagebox.askyesno("Latency Test", "Did you notice any delay?")
        
        # Convert response to 'yes' or 'no'
        response_text = "yes" if response else "no"

        # Record the response
        responses[entry_name] = response_text

        # Print the response to the console
        print(f"{entry_name}: {response_text} (Actual Latency: {actual_latency} ms)")

        # If all entries have been submitted, save responses to the log file
        if len(responses) == len(latencies):
            with open("results.log", "a") as file:
                log_entry = ",".join([f"{entry}:{response}" for entry, response in responses.items()])
                file.write(log_entry + "\n")
            print("Responses saved to results.log")

    # Schedule the popup after the specified latency
    root.after(latency_ms, show_popup)

# Create the main window
root = tk.Tk()
root.title("Latency Perception Test")

# Create text entry boxes in a row
for i, latency in enumerate(latencies):
    entry_name = f"TextBox {i + 1}"
    label = tk.Label(root, text=entry_name)
    label.grid(row=0, column=i, padx=5, pady=5)

    entry = tk.Entry(root)
    entry.grid(row=1, column=i, padx=5, pady=5)

    # Bind the Enter key to the text_entry_submit function
    entry.bind("<Return>", lambda event, name=entry_name, l=latency: text_entry_submit(name, l))

# Start the GUI event loop
root.mainloop()
