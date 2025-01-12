import pynvml
import time

# Initialize NVML
pynvml.nvmlInit()

# Get handle for the first GPU
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

print("Monitoring GPU Encoder Utilization... Press Ctrl+C to stop.")

try:
    while True:
        # Get encoder utilization
        encoder_util, sampling_period = pynvml.nvmlDeviceGetEncoderUtilization(handle)
        print(f"Encoder Utilization: {encoder_util}%")
        
        # Sleep for 1 second
        time.sleep(1)
except KeyboardInterrupt:
    print("\nMonitoring stopped.")

# Shutdown NVML
pynvml.nvmlShutdown()
