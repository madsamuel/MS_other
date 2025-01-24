import psutil
import time

def get_bandwidth_usage(interval=1):
    # Get initial network stats
    net_io_before = psutil.net_io_counters()
    time.sleep(interval)
    # Get stats after interval
    net_io_after = psutil.net_io_counters()
    
    # Calculate the bandwidth usage in bytes
    sent_bytes = net_io_after.bytes_sent - net_io_before.bytes_sent
    received_bytes = net_io_after.bytes_recv - net_io_before.bytes_recv
    
    sent_usage = sent_bytes / (1024 * 1024)  # Convert to MB
    received_usage = received_bytes / (1024 * 1024)  # Convert to MB

    return sent_usage, received_usage

def monitor_bandwidth():
    total_sent = 0
    total_received = 0

    print("Monitoring actual bandwidth usage. Press Ctrl+C to stop.")
    try:
        while True:
            sent, received = get_bandwidth_usage()
            total_sent += sent
            total_received += received

            print(f"Sent: {sent:.2f} MB, Received: {received:.2f} MB, "
                  f"Total Sent: {total_sent:.2f} MB, Total Received: {total_received:.2f} MB")

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        print(f"Total Bandwidth Usage - Sent: {total_sent:.2f} MB, Received: {total_received:.2f} MB")

if __name__ == "__main__":
    monitor_bandwidth()
