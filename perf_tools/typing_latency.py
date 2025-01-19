import tkinter as tk
from tkinter import messagebox
import random

# Define delays for text boxes in milliseconds and shuffle them for random assignment
# This ensures a varied user experience across text boxes
delays = [0, 100, 200, 300, 400, 500, 600]
random.shuffle(delays)
results = []

# List to store text box widgets for reference and manipulation
text_boxes = []

# Function to handle delayed typing in text boxes
def delayed_typing(entry, char, delay):
    """
    Inserts the typed character into the text box after the specified delay.
    This simulates typing latency for user experience evaluation.
    """
    def update_text():
        entry.insert(tk.END, char)

    if char.isprintable():
        root.after(delay, update_text)
        return "break"

# Function to handle input submission on pressing Enter
def handle_input(entry, delay, index):
    """
    Handles user input by capturing the text, clearing the text box,
    and prompting the user to confirm whether they noticed a delay.
    """
    user_input = entry.get()
    entry.delete(0, tk.END)
    response = messagebox.askyesno(
        "Typing Latency Test",
        f"Did you notice a delay in Text Box {index + 1}?"
    )
    result = f"Text Box {index + 1}-{delay}ms:{'Yes' if response else 'No'}"
    results.append(result)

# Function to reset all text boxes and reshuffle delay values
def reset_all_text_boxes():
    """
    Resets all text boxes to an empty state, reshuffles delay assignments,
    and clears previously recorded results.
    """
    global delays, results
    random.shuffle(delays)
    results.clear()
    for text_box in text_boxes:
        text_box.delete(0, tk.END)
    messagebox.showinfo("Typing Latency Test", "Text boxes reset and delays reshuffled!")

# Function to finalize the test and save results to a file
def finish_test():
    """
    Checks if all text boxes have been used, saves results to a file,
    and resets the test environment.
    """
    if len(results) == len(delays):
        with open("typing_latency_test_results.txt", "a") as file:
            file.write(",".join(results) + "\n")
        reset_all_text_boxes()

# Create the main application window
root = tk.Tk()
root.title("Typing Latency Test")

# Create and configure the menu bar
menu_bar = tk.Menu(root)

# Add "File" menu with an exit option
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add "Edit" menu with an option to reseed the delays
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Reseed", command=reset_all_text_boxes)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Apply the menu bar to the main window
root.config(menu=menu_bar)

# Create text boxes with assigned delays and corresponding labels
for i, delay in enumerate(delays):
    frame = tk.Frame(root)
    frame.pack(pady=10)

    label = tk.Label(frame, text=f"Text Box {i + 1}:")
    label.pack(side=tk.LEFT)

    entry = tk.Entry(frame, font=("Helvetica", 14))
    entry.pack(side=tk.LEFT, padx=10)

    # Store the text box for reference
    text_boxes.append(entry)

    # Bind keypress and Enter events to their respective handlers
    entry.bind("<KeyPress>", lambda event, e=entry, d=delay: delayed_typing(e, event.char, d))
    entry.bind("<Return>", lambda event, e=entry, d=delay, i=i: handle_input(e, d, i))

# Add a button to complete the test and save results
finish_button = tk.Button(root, text="Finish Test", command=finish_test)
finish_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
