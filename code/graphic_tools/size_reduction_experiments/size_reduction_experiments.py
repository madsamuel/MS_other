import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

class ImageCompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Compression UI")

        self.original_img = None
        self.compressed_img = None
        self.image_path = None

        self.setup_ui()

    def setup_ui(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        ttk.Button(control_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Save Compressed Image", command=self.save_image).pack(side=tk.LEFT, padx=5)

        self.quality_slider = ttk.Scale(control_frame, from_=10, to=95, orient=tk.HORIZONTAL, command=self.update_compression)
        self.quality_slider.set(75)
        self.quality_slider.pack(side=tk.LEFT, padx=5)

        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.original_canvas = tk.Canvas(self.canvas_frame, bg='gray')
        self.original_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.compressed_canvas = tk.Canvas(self.canvas_frame, bg='gray')
        self.compressed_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.original_canvas.bind('<Configure>', lambda event: self.resize_canvas(event, self.original_canvas, self.original_img))
        self.compressed_canvas.bind('<Configure>', lambda event: self.resize_canvas(event, self.compressed_canvas, self.compressed_img))

    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.image_path = path
            self.original_img = Image.open(path)
            self.resize_canvas(None, self.original_canvas, self.original_img)
            self.update_compression()

    def resize_canvas(self, event, canvas, img):
        canvas.delete("all")
        if img:
            canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()
            img_copy = img.copy()
            img_copy.thumbnail((canvas_width, canvas_height))
            photo = ImageTk.PhotoImage(img_copy)
            canvas.image = photo  # prevent garbage collection
            canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo)

    def update_compression(self, event=None):
        if self.original_img:
            quality = int(self.quality_slider.get())
            temp_path = "temp_compressed.jpg"
            img_to_save = self.original_img.convert('RGB')
            img_to_save.save(temp_path, 'JPEG', quality=quality, optimize=True)
            self.compressed_img = Image.open(temp_path)
            self.resize_canvas(None, self.compressed_canvas, self.compressed_img)
            os.remove(temp_path)

    def save_image(self):
        if self.compressed_img:
            path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
            if path:
                quality = int(self.quality_slider.get())
                img_to_save = self.original_img.convert('RGB')
                img_to_save.save(path, 'JPEG', quality=quality, optimize=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressionApp(root)
    root.mainloop()
