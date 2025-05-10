import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np

def ycbcr_subsample(img, subsample_type):
    img_ycbcr = img.convert('YCbCr')
    y, cb, cr = img_ycbcr.split()

    y_np = np.array(y)
    cb_np = np.array(cb)
    cr_np = np.array(cr)

    h, w = cb_np.shape
    if subsample_type == "4:2:2":
        cb_np[:, 1::2] = cb_np[:, ::2]
        cr_np[:, 1::2] = cr_np[:, ::2]
    elif subsample_type == "4:2:1":
        cb_np[:, 1::4] = cb_np[:, ::4]
        cr_np[:, 1::4] = cr_np[:, ::4]
    elif subsample_type == "4:2:0":
        cb_np[1::2, :] = cb_np[::2, :]
        cb_np[:, 1::2] = cb_np[:, ::2]
        cr_np[1::2, :] = cr_np[::2, :]
        cr_np[:, 1::2] = cr_np[:, ::2]
    elif subsample_type == "4:1:1":
        cb_np[:, 1::4] = cb_np[:, ::4]
        cr_np[:, 1::4] = cr_np[:, ::4]

    cb_new = Image.fromarray(cb_np, 'L')
    cr_new = Image.fromarray(cr_np, 'L')
    img_new = Image.merge("YCbCr", (y, cb_new, cr_new)).convert('RGB')
    return img_new

class SubsamplingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chroma Subsampling Visualizer")
        self.root.geometry("1000x600")

        self.img_original = None
        self.img_processed = None

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.subsample_var = tk.StringVar(value="4:2:2")
        ttk.Combobox(
            top_frame, textvariable=self.subsample_var, values=["4:2:2", "4:2:1", "4:2:0", "4:1:1"]
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Apply Subsampling", command=self.apply_subsampling).pack(side=tk.LEFT, padx=5)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_original = tk.Label(self.canvas_frame)
        self.canvas_original.pack(side=tk.LEFT, padx=10)

        self.canvas_processed = tk.Label(self.canvas_frame)
        self.canvas_processed.pack(side=tk.LEFT, padx=10)

    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.img_original = Image.open(path).convert("RGB")
        self.display_image(self.canvas_original, self.img_original)

    def apply_subsampling(self):
        if not self.img_original:
            return
        subsample_type = self.subsample_var.get()
        self.img_processed = ycbcr_subsample(self.img_original, subsample_type)
        self.display_image(self.canvas_processed, self.img_processed)

    def display_image(self, widget, img):
        max_size = (450, 450)
        img_resized = img.copy()
        img_resized.thumbnail(max_size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)
        widget.configure(image=photo)
        widget.image = photo

if __name__ == "__main__":
    root = tk.Tk()
    app = SubsamplingApp(root)
    root.mainloop()
