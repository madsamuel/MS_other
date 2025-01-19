import tkinter as tk
from tkinter import filedialog

class TextLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Loader")

        # Create text frame
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(pady=10)

        # Create text box with scrollbar
        self.text_box = tk.Text(self.text_frame, wrap="word", height=20, width=60)
        self.scrollbar = tk.Scrollbar(self.text_frame, orient="vertical", command=self.text_box.yview)
        self.text_box.config(yscrollcommand=self.scrollbar.set)
        self.text_box.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse scroll event with delay logic
        self.last_scroll_time = 0
        self.text_box.bind("<MouseWheel>", self.delayed_scroll)

        # Load button
        self.load_button = tk.Button(root, text="Load Text File", command=self.load_text)
        self.load_button.pack(pady=5)

        # Automatically load lorem_ipsum.txt
        self.load_default_text()

    def load_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self._load_from_file(file_path)

    def load_default_text(self):
        default_file = "lorem_ipsum.txt"
        try:
            self._load_from_file(default_file)
        except FileNotFoundError:
            self.text_box.insert(tk.END, "Error: lorem_ipsum.txt not found.")

    def _load_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, text_content)

    def delayed_scroll(self, event):
        import time
        current_time = time.time()
        if current_time - self.last_scroll_time > 0.1:
            self.text_box.yview_scroll(-1 * (event.delta // 120), "units")
            self.last_scroll_time = current_time
        return "break"

# Run the Tkinter app
root = tk.Tk()
app = TextLoaderApp(root)
root.mainloop()

