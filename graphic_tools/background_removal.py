import os
import onnxruntime as ort
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from rembg import remove
from PIL import Image, ImageTk

# Create the main app window
root = tk.Tk()
root.title("AI Background Remover")
root.geometry("500x500")

# Status bar at the bottom
status_bar = tk.Label(root, text="Ready", fg="black", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Frame for layout
frame = tk.Frame(root)
frame.pack(pady=20)

# Progress bar, hidden by default
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
progress_bar.pack_forget()

# Label to display images
img_label = tk.Label(root)
img_label.pack(pady=20)

def display_image(image_path: str) -> None:
    """Open and display an image in the UI."""
    image = Image.open(image_path)
    image.thumbnail((400, 400))  # Resize for display
    photo = ImageTk.PhotoImage(image)
    img_label.config(image=photo)
    img_label.image = photo  # Keep a reference to avoid GC

def remove_background() -> None:
    """Select an image and remove its background using rembg."""
    # Check available execution providers
    available_providers = ort.get_available_providers()
    if 'CUDAExecutionProvider' in available_providers:
        os.environ["ORT_DISABLE_TENSORRT"] = "1"
        os.environ["ORT_DISABLE_CPU"] = "0"
        os.environ["ORT_DISABLE_CUDA"] = "0"
        status_bar.config(text="Using CUDA + CPU")
    else:
        os.environ["ORT_DISABLE_TENSORRT"] = "1"
        os.environ["ORT_DISABLE_CPU"] = "0"
        os.environ["ORT_DISABLE_CUDA"] = "1"
        status_bar.config(text="Using CPU Only")

    # Ask user to select an image
    file_path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]  
    )
    if not file_path:
        return

    # Show progress bar
    progress_bar.pack(side=tk.BOTTOM, pady=5)
    status_bar.config(text="Processing...")
    progress_bar.start()
    root.update()

    # Display the selected image before processing
    display_image(file_path)

    # Compute the output path
    output_path = os.path.splitext(file_path)[0] + "-no-bgrd.png"

    # Perform background removal
    with open(file_path, "rb") as inp_file:
        input_data = inp_file.read()
        output_data = remove(input_data)

    # Write the result
    with open(output_path, "wb") as out_file:
        out_file.write(output_data)

    # Stop and hide the progress bar
    progress_bar.stop()
    progress_bar.pack_forget()

    # Update status
    status_bar.config(text="Done")

    # Display the processed image
    display_image(output_path)

    # Inform the user
    status_bar.config(text=f"Saved: {output_path}")
    messagebox.showinfo("Background Removed", f"Image successfully saved at: {output_path}")

# Button to start background removal
btn_select = tk.Button(frame, text="Select Image", command=remove_background)
btn_select.pack()

# Get the current directory where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the icon paths using the script directory
icon_path_ico = os.path.join(script_dir, "background_removal_icon.ico")
icon_path_png = os.path.join(script_dir, "background_removal_icon.png")


icon_path = "background_removal_icon.ico"  
try:
    root.iconbitmap(icon_path_ico)  # For Windows (.ico)
except tk.TclError:
    # For cross-platform support using .png
    from PIL import Image, ImageTk
    icon_image = ImageTk.PhotoImage(Image.open(icon_path_png))
    root.wm_iconphoto(True, icon_image)


root.mainloop()
