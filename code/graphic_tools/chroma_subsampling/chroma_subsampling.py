import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np

def ycbcr_subsample(img, subsample_type):
    if subsample_type == "4:4:4":
        return img

    img_ycbcr = img.convert('YCbCr')
    y, cb, cr = img_ycbcr.split()
    y_np = np.array(y)
    cb_np = np.array(cb)
    cr_np = np.array(cr)
    h, w = cb_np.shape

    def pad_to_even(arr, axis):
        if arr.shape[axis] % 2 != 0:
            pad_width = ((0, 1), (0, 0)) if axis == 0 else ((0, 0), (0, 1))
            arr = np.pad(arr, pad_width, mode='edge')
        return arr

    if subsample_type in ["4:2:2", "4:2:1", "4:1:1"]:
        cb_np = pad_to_even(cb_np, 1)
        cr_np = pad_to_even(cr_np, 1)
    elif subsample_type == "4:2:0":
        cb_np = pad_to_even(cb_np, 0)
        cb_np = pad_to_even(cb_np, 1)
        cr_np = pad_to_even(cr_np, 0)
        cr_np = pad_to_even(cr_np, 1)

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

    cb_new = Image.fromarray(cb_np[:h, :w], 'L')
    cr_new = Image.fromarray(cr_np[:h, :w], 'L')
    return Image.merge("YCbCr", (y, cb_new, cr_new)).convert('RGB')

class SubsamplingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chroma Subsampling Visualizer")
        self.root.geometry("1000x600")

        self.img_original = None
        self.img_processed = None
        self.zoom_original = 1.0
        self.zoom_processed = 1.0

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.subsample_var = tk.StringVar(value="4:4:4")
        ttk.Combobox(
            top_frame, textvariable=self.subsample_var, values=["4:4:4", "4:2:2", "4:2:1", "4:2:0", "4:1:1"]
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Apply Subsampling", command=self.apply_subsampling).pack(side=tk.LEFT, padx=5)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_original = tk.Canvas(self.canvas_frame, bg="black")
        self.canvas_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_processed = tk.Canvas(self.canvas_frame, bg="black")
        self.canvas_processed.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_original.bind("<MouseWheel>", lambda e: self.zoom(e, 'original'))
        self.canvas_processed.bind("<MouseWheel>", lambda e: self.zoom(e, 'processed'))

        self.root.bind("<Configure>", self.on_resize)

    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.img_original = Image.open(path).convert("RGB")
        self.zoom_original = 1.0
        self.zoom_processed = 1.0
        self.img_processed = None
        self.display_images()

    def apply_subsampling(self):
        if not self.img_original:
            return
        subsample_type = self.subsample_var.get()
        self.img_processed = ycbcr_subsample(self.img_original, subsample_type)
        self.zoom_processed = 1.0
        self.display_images()

    def display_images(self):
        self._draw_image_on_canvas(self.canvas_original, self.img_original, self.zoom_original)
        if self.img_processed:
            self._draw_image_on_canvas(self.canvas_processed, self.img_processed, self.zoom_processed)

    def _draw_image_on_canvas(self, canvas, img, zoom):
        canvas.delete("all")
        if img is None:
            return
        w = canvas.winfo_width()
        h = canvas.winfo_height()

        zoomed_size = (int(img.width * zoom), int(img.height * zoom))
        img_resized = img.resize(zoomed_size, Image.LANCZOS)

        photo = ImageTk.PhotoImage(img_resized)
        canvas.image = photo  # Prevent garbage collection
        x = (w - photo.width()) // 2
        y = (h - photo.height()) // 2
        canvas.create_image(x, y, image=photo, anchor=tk.NW)

    def zoom(self, event, which):
        delta = 0.1 if event.delta > 0 else -0.1
        if which == 'original':
            self.zoom_original = max(0.1, self.zoom_original + delta)
        elif which == 'processed':
            self.zoom_processed = max(0.1, self.zoom_processed + delta)
        self.display_images()

    def on_resize(self, event):
        self.display_images()

if __name__ == "__main__":
    root = tk.Tk()
    app = SubsamplingApp(root)
    root.mainloop()
