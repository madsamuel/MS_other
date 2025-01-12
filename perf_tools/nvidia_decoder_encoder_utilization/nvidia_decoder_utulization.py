import pynvml
import time

# Initialize NVML
pynvml.nvmlInit()

# Get handle for the first GPU
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

print("Monitoring GPU Decoder Utilization... Press Ctrl+C to stop.")

try:
    while True:
        # Get decoder utilization
        decoder_util, sampling_period = pynvml.nvmlDeviceGetDecoderUtilization(handle)
        print(f"Decoder Utilization: {decoder_util}%")
        
        # Sleep for 1 second
        time.sleep(1)
except KeyboardInterrupt:
    print("\nMonitoring stopped.")

# Shutdown NVML
pynvml.nvmlShutdown()
