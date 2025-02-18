import tkinter as tk
from tkinter import ttk, colorchooser

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Untitled - Paint")
        self.root.geometry("800x600")
        self.root.configure(bg="teal")

        # Draggable Window Container
        self.container = tk.Frame(self.root, bg="gray", width=800, height=600, relief="solid", borderwidth=2)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Dragging Window
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        self.title_bar = tk.Frame(self.container, bg="blue", height=30, relief="raised", bd=2)
        self.title_bar.pack(fill="x")
        self.title_bar.bind("<ButtonPress-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_drag)

        # Window Controls
        self.title_label = tk.Label(self.title_bar, text="Untitled - Paint", fg="white", bg="blue", padx=10)
        self.title_label.pack(side="left")

        self.btn_close = ttk.Button(self.title_bar, text="×", command=self.root.quit, width=2)
        self.btn_close.pack(side="right", padx=5)

        # Toolbar
        self.toolbar = tk.Frame(self.container, bg="lightgray", height=30)
        self.toolbar.pack(fill="x")

        self.brush_btn = ttk.Button(self.toolbar, text="Brush", command=lambda: self.set_tool("brush"))
        self.brush_btn.pack(side="left", padx=5)

        self.eraser_btn = ttk.Button(self.toolbar, text="Eraser", command=lambda: self.set_tool("eraser"))
        self.eraser_btn.pack(side="left", padx=5)

        self.color_btn = ttk.Button(self.toolbar, text="Color", command=self.choose_color)
        self.color_btn.pack(side="left", padx=5)

        # Canvas
        self.canvas = tk.Canvas(self.container, bg="white", width=780, height=500)
        self.canvas.pack(pady=5)

        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # Variables
        self.tool = "brush"
        self.color = "#000000"
        self.is_drawing = False

    def start_draw(self, event):
        self.is_drawing = True
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        if self.is_drawing:
            color = "#FFFFFF" if self.tool == "eraser" else self.color
            width = 10 if self.tool == "eraser" else 2
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=color, width=width, capstyle="round")
            self.last_x, self.last_y = event.x, event.y

    def stop_draw(self, event):
        self.is_drawing = False

    def choose_color(self):
        self.color = colorchooser.askcolor(title="Choose Color")[1] or self.color

    def set_tool(self, tool):
        self.tool = tool

    def start_drag(self, event):
        self.dragging = True
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag(self, event):
        if self.dragging:
            x = self.root.winfo_pointerx() - self.offset_x
            y = self.root.winfo_pointery() - self.offset_y
            self.container.place(x=x, y=y)

    def stop_drag(self, event):
        self.dragging = False

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
