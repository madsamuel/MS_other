import tkinter as tk
from tkinter import messagebox

# Define delays for each text box in milliseconds
delays = [0, 100, 200, 300, 400, 500, 600]
results = []

# Function to handle delayed typing
def delayed_typing(entry, char, delay):
    # Append the character with the specified delay
    def update_text():
        entry.insert(tk.END, char)

    # Only process printable characters and prevent immediate display
    if char.isprintable():
        root.after(delay, update_text)
        return "break"

# Function to handle when Enter is pressed
def handle_input(entry, delay, index):
    user_input = entry.get()
    entry.delete(0, tk.END)

    # Ask the user if they noticed the delay
    response = messagebox.askyesno("Typing Latency Test", f"Did you notice a delay in Text Box {index + 1}?")
    result = f"Text Box {index + 1}:{'Yes' if response else 'No'}"
    results.append(result)


    # Save results to a file in the desired format
    if len(results) == len(delays):  # Only write to file once all boxes are completed
        with open("typing_latency_test_results.txt", "w") as file:
            file.write(",".join(results))

# Create the main window
root = tk.Tk()
root.title("Typing Latency Test")

# Create text boxes with different delays
for i, delay in enumerate(delays):
    frame = tk.Frame(root)
    frame.pack(pady=10)

    label = tk.Label(frame, text=f"Text Box {i + 1} (Delay: {delay} ms):")
    label.pack(side=tk.LEFT)

    entry = tk.Entry(frame, font=("Helvetica", 14))
    entry.pack(side=tk.LEFT, padx=10)

    # Bind key press events for delayed typing
    entry.bind("<KeyPress>", lambda event, e=entry, d=delay: delayed_typing(e, event.char, d))

    # Bind Enter key to handle input and show popup
    entry.bind("<Return>", lambda event, e=entry, d=delay, i=i: handle_input(e, d, i))

# Run the GUI event loop
root.mainloop()
