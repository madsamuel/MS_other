import psutil
import time

def get_bandwidth_usage(interval=1):
    # Get initial network stats
    net_io_before = psutil.net_io_counters()
    time.sleep(interval)
    # Get stats after interval
    net_io_after = psutil.net_io_counters()
    
    # Calculate the bandwidth usage
    sent_bytes = net_io_after.bytes_sent - net_io_before.bytes_sent
    received_bytes = net_io_after.bytes_recv - net_io_before.bytes_recv
    
    sent_speed = sent_bytes / interval / 1024  # Convert to KB/s
    received_speed = received_bytes / interval / 1024  # Convert to KB/s

    return sent_speed, received_speed

if __name__ == "__main__":
    print("Measuring bandwidth usage. Press Ctrl+C to stop.")
    try:
        while True:
            sent, received = get_bandwidth_usage()
            print(f"Upload Speed: {sent:.2f} KB/s, Download Speed: {received:.2f} KB/s")
    except KeyboardInterrupt:
        print("\nMeasurement stopped.")
