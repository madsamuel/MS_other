import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np

# Global variable to store the loaded image
loaded_img = None

# Function to perform subsampling (average block)
def subsample_image(img_array, block_size):
    h, w, c = img_array.shape
    h = (h // block_size) * block_size
    w = (w // block_size) * block_size
    img_array = img_array[:h, :w]
    img_array = img_array.reshape(h // block_size, block_size, w // block_size, block_size, c)
    return img_array.mean(axis=(1, 3)).astype(np.uint8)

# Function to perform downsampling (pick top-left pixel)
def downsample_image(img_array, block_size):
    return img_array[::block_size, ::block_size]

# Function to process the image with the current block size
def process_image():
    if loaded_img is None:
        return

    block_size = int(block_size_var.get())
    img_array = np.array(loaded_img)

    subsampled = subsample_image(img_array, block_size)
    downsampled = downsample_image(img_array, block_size)

    subsampled_img = Image.fromarray(subsampled)
    downsampled_img = Image.fromarray(downsampled)

    def resize_image(image, max_size=300):
        ratio = min(max_size / image.width, max_size / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size)

    original_img = ImageTk.PhotoImage(image=resize_image(loaded_img))
    subsampled_img = ImageTk.PhotoImage(image=resize_image(subsampled_img))
    downsampled_img = ImageTk.PhotoImage(image=resize_image(downsampled_img))

    original_title.grid(row=0, column=0, padx=10, pady=(0, 5))
    original_label.config(image=original_img)
    original_label.image = original_img

    subsampled_title.grid(row=0, column=1, padx=10, pady=(0, 5))
    subsampled_label.config(image=subsampled_img)
    subsampled_label.image = subsampled_img

    downsampled_title.grid(row=0, column=2, padx=10, pady=(0, 5))
    downsampled_label.config(image=downsampled_img)
    downsampled_label.image = downsampled_img

# Function to load the image
def load_image():
    global loaded_img
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return

    img = Image.open(file_path)
    img = ImageOps.exif_transpose(img)
    loaded_img = img
    process_image()

# Setup main window
root = tk.Tk()
root.title("Image Subsampling vs Downsampling")

# Load Button and Block Size
controls_frame = tk.Frame(root)
controls_frame.pack(pady=10)

load_button = tk.Button(controls_frame, text="Load Image", command=load_image)
load_button.pack(side="left", padx=5)

block_size_var = tk.StringVar(value="2")
block_size_label = tk.Label(controls_frame, text="Block Size:")
block_size_label.pack(side="left", padx=5)
block_size_combo = ttk.Combobox(controls_frame, textvariable=block_size_var, values=["2", "4", "8", "16", "32", "64"], width=5)
block_size_combo.pack(side="left", padx=5)
block_size_combo.bind("<<ComboboxSelected>>", lambda e: process_image())

# Frame to organize images and labels
frame = tk.Frame(root)
frame.pack()

# Labels with titles and images
original_title = tk.Label(frame, text="Original")
original_title.grid_remove()
original_label = tk.Label(frame)
original_label.grid(row=1, column=0, padx=10)

subsampled_title = tk.Label(frame, text="Subsampled")
subsampled_title.grid_remove()
subsampled_label = tk.Label(frame)
subsampled_label.grid(row=1, column=1, padx=10)

downsampled_title = tk.Label(frame, text="Downsampled")
downsampled_title.grid_remove()
downsampled_label = tk.Label(frame)
downsampled_label.grid(row=1, column=2, padx=10)

# Start the UI loop
root.mainloop()
