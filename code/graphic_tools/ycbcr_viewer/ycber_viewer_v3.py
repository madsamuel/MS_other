import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

# Function to load and process the image
def load_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return

    img = Image.open(file_path)
    img_ycbcr = img.convert('YCbCr')
    y, cb, cr = img_ycbcr.split()

    # Maintain aspect ratio and resize
    def resize_image(image, max_size=300):
        ratio = min(max_size / image.width, max_size / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size)

    original_img = ImageTk.PhotoImage(image=resize_image(img))
    y_img = ImageTk.PhotoImage(image=resize_image(y))
    cb_img = ImageTk.PhotoImage(image=resize_image(cb))
    cr_img = ImageTk.PhotoImage(image=resize_image(cr))

    # Update UI images
    original_label.config(image=original_img)
    original_label.image = original_img
    original_title.grid()

    y_label.config(image=y_img)
    y_label.image = y_img
    y_title.grid()

    cb_label.config(image=cb_img)
    cb_label.image = cb_img
    cb_title.grid()

    cr_label.config(image=cr_img)
    cr_label.image = cr_img
    cr_title.grid()

# Setup main window
root = tk.Tk()
root.title("YCbCr Channel Viewer")

# Load Button
load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack(pady=10)

# Frame to organize images and labels
frame = tk.Frame(root)
frame.pack()

# Labels with titles and images
original_title = tk.Label(frame, text="Original")
original_title.grid_remove()
original_label = tk.Label(frame)
original_label.grid(row=1, column=0, padx=10)

y_title = tk.Label(frame, text="Y Channel")
y_title.grid_remove()
y_label = tk.Label(frame)
y_label.grid(row=1, column=1, padx=10)

cb_title = tk.Label(frame, text="Cb Channel")
cb_title.grid_remove()
cb_label = tk.Label(frame)
cb_label.grid(row=1, column=2, padx=10)

cr_title = tk.Label(frame, text="Cr Channel")
cr_title.grid_remove()
cr_label = tk.Label(frame)
cr_label.grid(row=1, column=3, padx=10)

# Start the UI loop
root.mainloop()