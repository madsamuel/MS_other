import pynvml
import time

# Initialize NVML
pynvml.nvmlInit()

# Get handle for the first GPU
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

# Generate log file name with current date
date_str = time.strftime("%Y-%m-%d")
log_file = f"encoder_log_{date_str}.txt"

print("Monitoring GPU Encoder Utilization... Press Ctrl+C to stop.")

last_logged_encoder_utilization = None  # To track the last logged value

try:
    with open(log_file, "a") as log:
        while True:
            # Get encoder utilization
            encoder_util, sampling_period = pynvml.nvmlDeviceGetEncoderUtilization(handle)
            print(f"Encoder Utilization: {encoder_util}%")

            # Get the current timestamp
            timestamp = time.strftime("%H:%M:%S")

            # Log only if the utilization changes
            if encoder_util != last_logged_encoder_utilization:
                log.write(f"{timestamp} - {encoder_util}%\n")
                log.flush()  # Ensure the log is written to file immediately
                last_logged_encoder_utilization = encoder_util

            # Sleep for 1 second
            time.sleep(1)
except KeyboardInterrupt:
    print("\nMonitoring stopped.")
    pynvml.nvmlShutdown()
