import os
import tkinter as tk
from tkinter import filedialog
from rembg import remove
from PIL import Image, ImageTk

def remove_background():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
    if not file_path:
        return
    
    output_path = os.path.splitext(file_path)[0] + "-no-bgrd.png"
    
    with open(file_path, "rb") as inp_file:
        input_data = inp_file.read()
        output_data = remove(input_data)
    
    with open(output_path, "wb") as out_file:
        out_file.write(output_data)
    
    display_image(output_path)
    
    status_label.config(text=f"Saved: {output_path}")

def display_image(image_path):
    image = Image.open(image_path)
    image.thumbnail((400, 400))  # Resize for display
    photo = ImageTk.PhotoImage(image)
    img_label.config(image=photo)
    img_label.image = photo

# UI Setup
root = tk.Tk()
root.title("AI Background Remover")
root.geometry("500x500")

frame = tk.Frame(root)
frame.pack(pady=20)

btn_select = tk.Button(frame, text="Select Image", command=remove_background)
btn_select.pack()

img_label = tk.Label(root)
img_label.pack(pady=20)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
