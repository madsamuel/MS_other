import pynvml
import time
import os

# Initialize NVML
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

# Get GPU handle
handle = initialize_nvml()

# Generate log file name with current date
date_str = time.strftime("%Y-%m-%d")
log_file = f"decoder_log_{date_str}.txt"
last_logged_utilization = None  # To track the last logged value

print("Monitoring GPU Decoder Utilization... Press Ctrl+C to stop.")

try:
    with open(log_file, "a") as log:
        while True:
            try:
                # Get decoder utilization
                decoder_util, _ = pynvml.nvmlDeviceGetDecoderUtilization(handle)
                
                # Get the current timestamp
                timestamp = time.strftime("%H:%M:%S")

                # Log only if the utilization changes
                if decoder_util != last_logged_utilization:
                    log.write(f"{timestamp} - {decoder_util}%\n")
                    log.flush()  # Ensure immediate writing to file
                    last_logged_utilization = decoder_util

                print(f"Decoder Utilization: {decoder_util}%")
                time.sleep(1)

            except pynvml.NVMLError as e:
                print(f"Error retrieving decoder utilization: {str(e)}")
except KeyboardInterrupt:
    print("\nMonitoring stopped.")
    pynvml.nvmlShutdown()
