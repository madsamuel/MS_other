import os
import tkinter as tk
from tkinter import filedialog
from rembg import remove
from PIL import Image, ImageTk
from tkinter import ttk
import onnxruntime as ort

def remove_background():
    from tkinter import ttk
    
    # Check available execution providers
    available_providers = ort.get_available_providers()
    if 'CUDAExecutionProvider' in available_providers:
        os.environ["ORT_DISABLE_TENSORRT"] = "1"
        os.environ["ORT_DISABLE_CPU"] = "0"
        os.environ["ORT_DISABLE_CUDA"] = "0"
        status_label.config(text="Using CUDA + CPU")
    else:
        os.environ["ORT_DISABLE_TENSORRT"] = "1"
        os.environ["ORT_DISABLE_CPU"] = "0"
        os.environ["ORT_DISABLE_CUDA"] = "1"
        status_label.config(text="Using CPU Only")
    from tkinter import ttk
    
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
    if not file_path:
        return
    
    output_path = os.path.splitext(file_path)[0] + "-no-bgrd.png"
    
    progress_bar.start()
    root.update()
    
    display_image(file_path)  # Show selected image before processing
    
    with open(file_path, "rb") as inp_file:
        input_data = inp_file.read()
        output_data = remove(input_data)
    
    with open(output_path, "wb") as out_file:
        out_file.write(output_data)
    
    progress_bar.stop()
    display_image(output_path)
    
    status_label.config(text=f"Saved: {output_path}")
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
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
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
progress_bar.pack(pady=10)
frame.pack(pady=20)

btn_select = tk.Button(frame, text="Select Image", command=remove_background)
btn_select.pack()

img_label = tk.Label(root)
img_label.pack(pady=20)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
