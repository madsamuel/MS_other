import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np
import cv2


class ImageEncoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Encoder with Adjustable QP")
        self.root.geometry("900x600")

        self.loaded_img = None
        self.encoded_img = None

        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=10)

        tk.Button(controls_frame, text="Load Image", command=self.load_image).pack(side="left", padx=5)

        tk.Label(controls_frame, text="Quality (QP):").pack(side="left", padx=5)
        self.quality_var = tk.IntVar(value=90)
        quality_slider = tk.Scale(
            controls_frame, from_=10, to=100, orient="horizontal", variable=self.quality_var,
            command=lambda _: self.process_image()
        )
        quality_slider.pack(side="left", padx=5)

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        self.frame.columnconfigure((0, 1), weight=1)

        self.original_title = tk.Label(self.frame, text="Original")
        self.original_label = tk.Label(self.frame)
        self.encoded_title = tk.Label(self.frame, text="Encoded")
        self.encoded_label = tk.Label(self.frame)

    def bind_events(self):
        self.root.bind("<Configure>", lambda _: self.update_display())

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not file_path:
            return

        try:
            img = Image.open(file_path)
            self.loaded_img = ImageOps.exif_transpose(img)
            self.process_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")
    
    def encode_image(self, img_array_bgr, quality):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encimg = cv2.imencode('.jpg', img_array_bgr, encode_param)
        decoded_img = cv2.imdecode(encimg, cv2.IMREAD_COLOR)
        return decoded_img


    def process_image(self):
        if self.loaded_img is None:
            return

        quality = int(self.quality_var.get())
        
        # Convert PIL RGB image to OpenCV BGR
        img_array = np.array(self.loaded_img)
        img_array_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # Encode and decode with OpenCV
        encoded_array = self.encode_image(img_array_bgr, quality)

        # Convert the resulting BGR array back to RGB for PIL
        encoded_array_rgb = cv2.cvtColor(encoded_array, cv2.COLOR_BGR2RGB)
        
        self.encoded_img = Image.fromarray(encoded_array_rgb)
        self.update_display()



    def resize_image(self, image, max_width, max_height):
        ratio = min(max_width / image.width, max_height / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size, Image.LANCZOS)

    def update_display(self):
        if self.loaded_img is None or self.encoded_img is None:
            return

        frame_width = self.frame.winfo_width() // 2 - 20
        frame_height = self.frame.winfo_height() - 80

        original_resized = ImageTk.PhotoImage(
            self.resize_image(self.loaded_img, frame_width, frame_height)
        )
        encoded_resized = ImageTk.PhotoImage(
            self.resize_image(self.encoded_img, frame_width, frame_height)
        )

        self.original_title.grid(row=0, column=0, pady=(0, 5))
        self.original_label.config(image=original_resized)
        self.original_label.image = original_resized
        self.original_label.grid(row=1, column=0, padx=10)

        self.encoded_title.grid(row=0, column=1, pady=(0, 5))
        self.encoded_label.config(image=encoded_resized)
        self.encoded_label.image = encoded_resized
        self.encoded_label.grid(row=1, column=1, padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEncoderApp(root)
    root.mainloop()
