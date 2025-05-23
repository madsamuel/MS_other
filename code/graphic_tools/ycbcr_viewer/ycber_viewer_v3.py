import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import numpy as np

# Function to load and process the image
def load_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return

    img = Image.open(file_path)
    img = ImageOps.exif_transpose(img)  # Fix orientation based on EXIF
    img_ycbcr = img.convert('YCbCr')
    y, cb, cr = img_ycbcr.split()

    # Create proper visualization for Cb and Cr channels
    cb_array = np.array(cb).astype(np.float32)
    cb_visual = np.stack([
        np.full(cb_array.shape, 128, dtype=np.float32),  # Red
        np.full(cb_array.shape, 128, dtype=np.float32),  # Green
        128 + (cb_array - 128)                          # Blue
    ], axis=-1).clip(0, 255).astype(np.uint8)

    cr_array = np.array(cr).astype(np.float32)
    cr_visual = np.stack([
        128 + (cr_array - 128),                          # Red
        np.full(cr_array.shape, 128, dtype=np.float32),  # Green
        np.full(cr_array.shape, 128, dtype=np.float32)   # Blue
    ], axis=-1).clip(0, 255).astype(np.uint8)

    cb_colored = Image.fromarray(cb_visual, mode='RGB')
    cr_colored = Image.fromarray(cr_visual, mode='RGB')

    # Maintain aspect ratio and resize
    def resize_image(image, max_size=300):
        ratio = min(max_size / image.width, max_size / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size)

    original_img = ImageTk.PhotoImage(image=resize_image(img))
    y_img = ImageTk.PhotoImage(image=resize_image(y))
    cb_img = ImageTk.PhotoImage(image=resize_image(cb_colored))
    cr_img = ImageTk.PhotoImage(image=resize_image(cr_colored))

    # Update UI images
    original_title.grid(row=0, column=0, padx=10, pady=(0, 5))
    original_label.config(image=original_img)
    original_label.image = original_img

    y_title.grid(row=0, column=1, padx=10, pady=(0, 5))
    y_label.config(image=y_img)
    y_label.image = y_img

    cb_title.grid(row=0, column=2, padx=10, pady=(0, 5))
    cb_label.config(image=cb_img)
    cb_label.image = cb_img

    cr_title.grid(row=0, column=3, padx=10, pady=(0, 5))
    cr_label.config(image=cr_img)
    cr_label.image = cr_img

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
