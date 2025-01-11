import tkinter as tk
from tkinter import messagebox
import random

# Define delays for text boxes in milliseconds
delays = [0, 100, 200, 300, 400, 500, 600]
random.shuffle(delays)
results = []

# Keep track of text box widgets
text_boxes = []

# Function to handle delayed typing
def delayed_typing(entry, char, delay):
    def update_text():
        entry.insert(tk.END, char)
    if char.isprintable():
        root.after(delay, update_text)
        return "break"

# Function to handle when Enter is pressed
def handle_input(entry, delay, index):
    user_input = entry.get()
    entry.delete(0, tk.END)
    response = messagebox.askyesno("Typing Latency Test", f"Did you notice a delay in Text Box {index + 1}?")
    result = f"Text Box {index + 1}-{delay}ms:{'Yes' if response else 'No'}"
    results.append(result)

# Function to reset all text boxes and reshuffle delays
def reset_all_text_boxes():
    global delays, results
    random.shuffle(delays)
    results.clear()
    for text_box in text_boxes:
        text_box.delete(0, tk.END)
    messagebox.showinfo("Typing Latency Test", "Text boxes reset and delays reshuffled!")

# Function to finish the test and write results to a file
def finish_test():
    if len(results) == len(delays):
        with open("typing_latency_test_results.txt", "a") as file:
            file.write(",".join(results) + "\n")
        reset_all_text_boxes()

# Create the main window
root = tk.Tk()
root.title("Typing Latency Test")

# Create the menu bar
menu_bar = tk.Menu(root)

# Add File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add Edit menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Reseed", command=reset_all_text_boxes)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Configure the menu bar
root.config(menu=menu_bar)

# Create text boxes with different delays
for i, delay in enumerate(delays):
    frame = tk.Frame(root)
    frame.pack(pady=10)
    label = tk.Label(frame, text=f"Text Box {i + 1}:")
    label.pack(side=tk.LEFT)
    entry = tk.Entry(frame, font=("Helvetica", 14))
    entry.pack(side=tk.LEFT, padx=10)

    # Keep a reference to each text box
    text_boxes.append(entry)

    entry.bind("<KeyPress>", lambda event, e=entry, d=delay: delayed_typing(e, event.char, d))
    entry.bind("<Return>", lambda event, e=entry, d=delay, i=i: handle_input(e, d, i))

# Add the "Finish Test" button
finish_button = tk.Button(root, text="Finish Test", command=finish_test)
finish_button.pack(pady=20)

# Run the GUI event loop
root.mainloop()
