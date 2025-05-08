import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2
from skimage.metrics import structural_similarity as compare_ssim
from math import log10

def load_image(path):
    image = cv2.imread(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def immse(img1, img2):
    return np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)

def psnr(img1, img2):
    mse = immse(img1, img2)
    if mse == 0:
        return float('inf')
    PIXEL_MAX = 255.0
    return 20 * log10(PIXEL_MAX / np.sqrt(mse))

def ssim(img1, img2):
    return compare_ssim(img1, img2, channel_axis=-1)

def estimate_qp(mse):
    return min(51, max(0, 2.0 * np.log1p(mse)))  # Heuristic formula

class ImageCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Comparison & QP Estimator")

        self.image1 = None
        self.image2 = None

        # Buttons
        tk.Button(root, text="Load Image A", command=self.load_image_a, width=20).pack()
        tk.Button(root, text="Load Image B", command=self.load_image_b, width=20).pack()

        # Panels
        self.panel_a = tk.Label(root)
        self.panel_a.pack(side="left", padx=10, pady=10)

        self.panel_b = tk.Label(root)
        self.panel_b.pack(side="left", padx=10, pady=10)

        # Result display
        self.result_label = tk.Label(root, text="Load two images to compare", font=("Arial", 12), justify="left")
        self.result_label.pack(pady=10)

    def display_image(self, panel, image):
        im = Image.fromarray(image).resize((256, 256))
        photo = ImageTk.PhotoImage(im)
        panel.configure(image=photo)
        panel.image = photo

    def load_image_a(self):
        path = filedialog.askopenfilename()
        if path:
            self.image1 = load_image(path)
            self.display_image(self.panel_a, self.image1)
            self.try_compute()

    def load_image_b(self):
        path = filedialog.askopenfilename()
        if path:
            self.image2 = load_image(path)
            self.display_image(self.panel_b, self.image2)
            self.try_compute()

    def try_compute(self):
        if self.image1 is not None and self.image2 is not None:
            try:
                if self.image1.shape != self.image2.shape:
                    self.image2 = cv2.resize(self.image2, (self.image1.shape[1], self.image1.shape[0]))

                mse_val = immse(self.image1, self.image2)
                psnr_val = psnr(self.image1, self.image2)
                ssim_val = ssim(self.image1, self.image2)
                qp_val = estimate_qp(mse_val)

                text = (
                    f"IMMSE: {mse_val:.2f}\n"
                    f"PSNR: {psnr_val:.2f} dB\n"
                    f"SSIM: {ssim_val:.4f}\n"
                    f"Estimated QP: {qp_val:.1f}"
                )
                self.result_label.config(text=text)
            except Exception as e:
                self.result_label.config(text=f"Error: {e}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompareApp(root)
    root.mainloop()
