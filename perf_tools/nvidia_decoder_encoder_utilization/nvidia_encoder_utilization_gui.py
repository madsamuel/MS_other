import pynvml
import time
import threading
import tkinter as tk
from pystray import Icon, MenuItem, Menu
from PIL import Image
import os

# Global variable to track encoder utilization
encoder_utilization = 0
running = True
counter_window = None
last_logged_encoder_utilization = None  # To track the last logged value

# Generate log file name with current date
date_str = time.strftime("%Y-%m-%d")
log_file = f"encoder_log_{date_str}.txt"  # Log file name

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

# Function to monitor GPU encoder utilization and log changes
def monitor_encoder():
    global encoder_utilization, running, last_logged_encoder_utilization
    with open(log_file, "a") as log:
        while running:
            try:
                util, _ = pynvml.nvmlDeviceGetEncoderUtilization(handle)
                encoder_utilization = util

                # Get the current timestamp
                timestamp = time.strftime("%H:%M:%S")

                # Log only if the utilization changes
                if encoder_utilization != last_logged_encoder_utilization:
                    log.write(f"{timestamp} - {encoder_utilization}%\n")
                    log.flush()  # Ensure the log is written to file immediately
                    last_logged_encoder_utilization = encoder_utilization

            except pynvml.NVMLError as e:
                print(f"Error retrieving encoder utilization: {str(e)}")
            time.sleep(1)

# Function to display the encoder utilization on screen
def show_counter():
    global counter_window
    if counter_window is not None:
        return  # Counter is already visible

    counter_window = tk.Tk()
    counter_window.title("Encoder Utilization")
    counter_window.overrideredirect(True)  # Remove window decorations
    counter_window.attributes("-topmost", True)  # Keep on top
    counter_window.attributes("-transparentcolor", "black")  # Set transparency color

    # Create a label with a transparent background
    label = tk.Label(
        counter_window,
        text="",
        font=("Arial", 14),
        fg="yellow",
        bg="black",  # This will be transparent
        padx=10,
        pady=5,
        anchor="w"  # Left-justify the text
    )
    label.pack(fill="both", expand=True)

    def update_label():
        label_text = f"Encoder: {encoder_utilization}%"
        label.config(text=label_text)
        # Dynamically adjust window size based on text length
        text_width = (len(label_text) + 10) * 12  # Adjust to account for E and % and padding
        counter_window.geometry(f"{text_width}x80+0+0")
        counter_window.after(1000, update_label)

    update_label()
    counter_window.mainloop()

# Function to hide the counter window
def hide_counter():
    global counter_window
    if counter_window is not None:
        counter_window.withdraw()
        counter_window = None

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
    # Use an external .ico file for the tray icon
    icon_image = Image.open("icon.ico")

    # Create a right-click menu for the tray icon
    menu = Menu(
        MenuItem("Show Counter", lambda: threading.Thread(target=show_counter).start()),
        MenuItem("Hide Counter", lambda: threading.Thread(target=hide_counter).start()),
        MenuItem("Exit", exit_app)
    )

    # Create the system tray icon
    icon = Icon("GPU Encoder Monitor", icon_image, menu=menu)
    icon.run()

# Start the background monitoring thread
monitor_thread = threading.Thread(target=monitor_encoder, daemon=True)
monitor_thread.start()

# Run the system tray icon
create_icon()
