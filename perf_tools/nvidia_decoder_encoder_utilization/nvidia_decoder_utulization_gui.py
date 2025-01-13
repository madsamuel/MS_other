import pynvml
import time
import threading
import tkinter as tk
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# Global variable to track decoder utilization
decoder_utilization = 0
running = True
counter_window = None

# Function to safely initialize NVML
def initialize_nvml():
    try:
        pynvml.nvmlInit()
        return pynvml.nvmlDeviceGetHandleByIndex(0)
    except pynvml.NVMLError_LibraryNotFound:
        print("Error: NVML library not found. Ensure NVIDIA drivers are installed.")
        exit(1)
    except pynvml.NVMLError_InsufficientPermissions:
        print("Error: Insufficient permissions to access NVML. Run the app as Administrator.")
        exit(1)
    except pynvml.NVMLError as e:
        print(f"Error initializing NVML: {str(e)}")
        exit(1)

# Initialize NVML and get the GPU handle
handle = initialize_nvml()

# Function to monitor GPU decoder utilization
def monitor_decoder():
    global decoder_utilization, running
    while running:
        try:
            util, _ = pynvml.nvmlDeviceGetDecoderUtilization(handle)
            decoder_utilization = util
        except pynvml.NVMLError as e:
            print(f"Error retrieving decoder utilization: {str(e)}")
        time.sleep(1)

# Function to display the decoder utilization on screen
def show_counter():
    global counter_window
    if counter_window is not None:
        return  # Counter is already visible

    counter_window = tk.Tk()
    counter_window.title("Decoder Utilization")
    counter_window.geometry("300x50+1000+50")
    counter_window.overrideredirect(True)  # Remove window decorations
    counter_window.attributes("-topmost", True)  # Keep on top
    counter_window.attributes("-transparentcolor", "black")  # Set transparency color

    # Create a label with a transparent background
    label = tk.Label(
        counter_window,
        text="",
        font=("Arial", 24),
        fg="yellow",
        bg="black",  # This will be transparent
        padx=10,
        pady=5
    )
    label.pack(fill="both", expand=True)

    def update_label():
        label.config(text=f"Decoder: {decoder_utilization}%")
        counter_window.after(1000, update_label)

    update_label()
    counter_window.mainloop()

# Function to hide the counter window
def hide_counter():
    global counter_window
    if counter_window is not None:
        counter_window.destroy()
        counter_window = None

# Function to dynamically update the tray menu
def update_menu(icon):
    if counter_window is None:
        return Menu(
            MenuItem("Show Counter", lambda: threading.Thread(target=show_counter).start()),
            MenuItem("Exit", exit_app)
        )
    else:
        return Menu(
            MenuItem("Hide Counter", hide_counter),
            MenuItem("Exit", exit_app)
        )

# Function to handle exiting the app
def exit_app(icon=None, item=None):
    global running
    running = False
    try:
        pynvml.nvmlShutdown()
    except pynvml.NVMLError:
        pass  # Ignore shutdown errors
    if icon:
        icon.stop()
    exit(0)

# Function to create the tray icon
def create_icon():
    # Create a blank icon image
    image = Image.new("RGB", (64, 64), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill=(255, 255, 0))

    # Create a right-click menu for the tray icon
    menu = Menu(
        MenuItem("Show Counter", lambda: threading.Thread(target=show_counter).start()),
        MenuItem("Exit", exit_app)
    )

    # Create the system tray icon
    icon = Icon("GPU Decoder Monitor", image, menu=menu)
    icon.run()

# Start the background monitoring thread
monitor_thread = threading.Thread(target=monitor_decoder, daemon=True)
monitor_thread.start()

# Run the system tray icon
create_icon()
