import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np

# Global variables
loaded_img = None
original_img = None
subsampled_img = None
downsampled_img = None

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
    global original_img, subsampled_img, downsampled_img
    if loaded_img is None:
        return

    block_size = int(block_size_var.get())
    img_array = np.array(loaded_img)

    subsampled = subsample_image(img_array, block_size)
    downsampled = downsample_image(img_array, block_size)

    subsampled_img = Image.fromarray(subsampled)
    downsampled_img = Image.fromarray(downsampled)

    update_display()

# Function to update image display
def update_display():
    if loaded_img is None:
        return

    frame.update_idletasks()
    frame_width = frame.winfo_width()
    frame_height = frame.winfo_height()

    width = frame_width // 3 - 20
    height = frame_height - 100

    def resize_image(image):
        ratio = min(width / image.width, height / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size)

    resized_original = ImageTk.PhotoImage(image=resize_image(loaded_img))
    resized_subsampled = ImageTk.PhotoImage(image=resize_image(subsampled_img))
    resized_downsampled = ImageTk.PhotoImage(image=resize_image(downsampled_img))

    original_title.grid(row=0, column=0, padx=10, pady=(0, 5), sticky="n")
    original_label.config(image=resized_original)
    original_label.image = resized_original
    original_label.grid(row=1, column=0, padx=10, pady=10, sticky="n")

    subsampled_title.grid(row=0, column=1, padx=10, pady=(0, 5), sticky="n")
    subsampled_label.config(image=resized_subsampled)
    subsampled_label.image = resized_subsampled
    subsampled_label.grid(row=1, column=1, padx=10, pady=10, sticky="n")

    downsampled_title.grid(row=0, column=2, padx=10, pady=(0, 5), sticky="n")
    downsampled_label.config(image=resized_downsampled)
    downsampled_label.image = resized_downsampled
    downsampled_label.grid(row=1, column=2, padx=10, pady=10, sticky="n")

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
root.geometry("900x600")

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
frame.pack(expand=True, fill="both")
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.columnconfigure(2, weight=1)

# Labels with titles and images
original_title = tk.Label(frame, text="Original")
original_label = tk.Label(frame)
subsampled_title = tk.Label(frame, text="Subsampled")
subsampled_label = tk.Label(frame)
downsampled_title = tk.Label(frame, text="Downsampled")
downsampled_label = tk.Label(frame)

# Bind window resize to update_display
root.bind("<Configure>", lambda event: update_display())

# Start the UI loop
root.mainloop()
