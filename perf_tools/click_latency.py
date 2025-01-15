import tkinter as tk
from tkinter import messagebox
import time

# Define latency values for each button in milliseconds
latencies = [0, 100, 200, 300, 400, 500, 600]

# Initialize an empty response dictionary
responses = {}

# Function to handle button clicks
def button_click(button_name, latency_ms):
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
        responses[button_name] = response_text
        
        # Print the response to the console
        print(f"{button_name}: {response_text} (Actual Latency: {actual_latency} ms)")
        
        # If all buttons have been clicked, save responses to the log file
        if len(responses) == len(latencies):
            with open("click_latency.log", "a") as file:
                log_entry = ",".join([f"{button}:{response}" for button, response in responses.items()])
                file.write(log_entry + "\n")
            print("Responses saved to click_latency.lg")
    
    # Schedule the popup after the specified latency using after()
    root.after(latency_ms, show_popup)

# Create the main window
root = tk.Tk()
root.title("Latency Perception Test")

# Create buttons in a row
for i, latency in enumerate(latencies):
    button_name = f"Button {i + 1}"
    button = tk.Button(root, text=button_name, command=lambda name=button_name, l=latency: button_click(name, l))
    button.grid(row=0, column=i, padx=10, pady=20)  # Use grid layout to arrange buttons in a row

# Start the GUI event loop
root.mainloop()
