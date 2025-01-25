import psutil
import time


def get_bandwidth_usage(interval=1):
    """
    Measure network bandwidth usage over a given interval.

    Parameters
    ----------
    interval : int
        Time interval in seconds over which to measure usage.

    Returns
    -------
    tuple
        A tuple of two floats: (sent_usage_in_mb, received_usage_in_mb).
        Represents the amount of data sent and received in MB during the interval.
    """
    # Capture initial stats
    net_io_before = psutil.net_io_counters()
    time.sleep(interval)
    # Capture stats after the interval
    net_io_after = psutil.net_io_counters()

    # Calculate the difference
    sent_bytes = net_io_after.bytes_sent - net_io_before.bytes_sent
    received_bytes = net_io_after.bytes_recv - net_io_before.bytes_recv

    # Convert bytes to MB
    sent_usage_mb = sent_bytes / (1024 * 1024)
    received_usage_mb = received_bytes / (1024 * 1024)

    return sent_usage_mb, received_usage_mb


def monitor_bandwidth(interval=1):
    """
    Continuously monitor and display cumulative network bandwidth usage.

    Parameters
    ----------
    interval : int
        Time interval in seconds between usage checks.
    """
    total_sent_mb = 0.0
    total_received_mb = 0.0

    print(f"Monitoring bandwidth usage every {interval} second(s). Press Ctrl+C to stop.")

    try:
        while True:
            sent_mb, received_mb = get_bandwidth_usage(interval=interval)
            total_sent_mb += sent_mb
            total_received_mb += received_mb

            print(
                f"Interval Sent: {sent_mb:.2f} MB, "
                f"Interval Received: {received_mb:.2f} MB, "
                f"Total Sent: {total_sent_mb:.2f} MB, "
                f"Total Received: {total_received_mb:.2f} MB"
            )

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        print(
            f"Final Bandwidth Usage - Sent: {total_sent_mb:.2f} MB, "
            f"Received: {total_received_mb:.2f} MB"
        )


if __name__ == "__main__":
    # You can modify the interval here if you want a different measurement frequency
    monitor_bandwidth(interval=1)
