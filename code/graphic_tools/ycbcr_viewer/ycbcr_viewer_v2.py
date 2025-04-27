import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def load_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", ("*.png", "*.jpg", "*.jpeg"))])
    if file_path:
        image = Image.open(file_path)
        display_image(image)
        ycbcr_image = image.convert("YCbCr")
        display_ycbcr_components(ycbcr_image)

def display_image(image):
    image.thumbnail((400, 400))
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo

def display_ycbcr_components(ycbcr_image):
    ycbcr_array = np.array(ycbcr_image)
    y_component = Image.fromarray(ycbcr_array[:, :, 0], 'L')
    cb_component = ycbcr_array[:, :, 1]
    cr_component = ycbcr_array[:, :, 2]

    # Normalize Cb and Cr components for color mapping
    cb_component_normalized = (cb_component - np.min(cb_component)) / (np.max(cb_component) - np.min(cb_component))
    cr_component_normalized = (cr_component - np.min(cr_component)) / (np.max(cr_component) - np.min(cr_component))

    # Apply color maps
    cb_colored = cm.bwr(cb_component_normalized)  # Blue-Yellow color map
    cr_colored = cm.seismic(cr_component_normalized)  # Red-Cyan color map

    # Convert to images
    cb_image = Image.fromarray((cb_colored[:, :, :3] * 255).astype(np.uint8))
    cr_image = Image.fromarray((cr_colored[:, :, :3] * 255).astype(np.uint8))

    y_photo = ImageTk.PhotoImage(y_component)
    cb_photo = ImageTk.PhotoImage(cb_image)
    cr_photo = ImageTk.PhotoImage(cr_image)

    y_label.config(image=y_photo)
    y_label.image = y_photo

    cb_label.config(image=cb_photo)
    cb_label.image = cb_photo

    cr_label.config(image=cr_photo)
    cr_label.image = cr_photo

# Create the main window
root = tk.Tk()
root.title("YCbCr Image Breakdown")

# Create a button to load an image
load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack(pady=10)

# Create labels to display the image and its YCbCr components
image_label = tk.Label(root)
image_label.pack(pady=10)

y_label = tk.Label(root)
y_label.pack(side=tk.LEFT, padx=10)

cb_label = tk.Label(root)
cb_label.pack(side=tk.LEFT, padx=10)

cr_label = tk.Label(root)
cr_label.pack(side=tk.LEFT, padx=10)

# Run the application
root.mainloop()
