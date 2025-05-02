import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np
import cv2

# Global variables
loaded_img = None
original_img = None
encoded_img = None

# Function to encode the image with a specified quality (QP)
def encode_image(img_array, quality):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, encimg = cv2.imencode('.jpg', img_array, encode_param)
    return cv2.imdecode(encimg, cv2.IMREAD_COLOR)

# Function to process the image with the current quality (QP)
def process_image():
    global original_img, encoded_img
    if loaded_img is None:
        return

    quality = int(quality_var.get())
    img_array = np.array(loaded_img)

    encoded = encode_image(img_array, quality)
    encoded_img = Image.fromarray(cv2.cvtColor(encoded, cv2.COLOR_BGR2RGB))

    update_display()

# Function to update image display
def update_display():
    if loaded_img is None:
        return

    frame.update_idletasks()
    frame_width = frame.winfo_width()
    frame_height = frame.winfo_height()

    width = frame_width // 2 - 20
    height = frame_height - 100

    def resize_image(image):
        ratio = min(width / image.width, height / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size)

    resized_original = ImageTk.PhotoImage(image=resize_image(loaded_img))
    resized_encoded = ImageTk.PhotoImage(image=resize_image(encoded_img))

    original_title.grid(row=0, column=0, padx=10, pady=(0, 5), sticky="n")
    original_label.config(image=resized_original)
    original_label.image = resized_original
    original_label.grid(row=1, column=0, padx=10, pady=10, sticky="n")

    encoded_title.grid(row=0, column=1, padx=10, pady=(0, 5), sticky="n")
    encoded_label.config(image=resized_encoded)
    encoded_label.image = resized_encoded
    encoded_label.grid(row=1, column=1, padx=10, pady=10, sticky="n")

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
root.title("Image Encoder with Adjustable QP")
root.geometry("900x600")

# Load Button and Quality (QP)
controls_frame = tk.Frame(root)
controls_frame.pack(pady=10)

load_button = tk.Button(controls_frame, text="Load Image", command=load_image)
load_button.pack(side="left", padx=5)

quality_var = tk.StringVar(value="90")
quality_label = tk.Label(controls_frame, text="Quality (QP):")
quality_label.pack(side="left", padx=5)
quality_combo = ttk.Combobox(controls_frame, textvariable=quality_var, values=["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"], width=5)
quality_combo.pack(side="left", padx=5)
quality_combo.bind("<<ComboboxSelected>>", lambda e: process_image())

# Frame to organize images and labels
frame = tk.Frame(root)
frame.pack(expand=True, fill="both")
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)

# Labels with titles and images
original_title = tk.Label(frame, text="Original")
original_label = tk.Label(frame)
encoded_title = tk.Label(frame, text="Encoded")
encoded_label = tk.Label(frame)

# Bind window resize to update_display
root.bind("<Configure>", lambda event: update_display())

# Start the UI loop
root.mainloop()
