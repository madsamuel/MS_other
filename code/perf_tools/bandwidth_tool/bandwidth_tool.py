import psutil
import time
import argparse
import csv
import sys


def parse_arguments():
    """
    Parse command-line arguments and return them.

    Returns
    -------
    argparse.Namespace
        Parsed arguments including interval, interface, threshold, and csv_output.
    """
    parser = argparse.ArgumentParser(
        description="Monitor network bandwidth usage."
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Time interval in seconds between usage checks (default: 1.0)"
    )
    parser.add_argument(
        "-n", "--interface",
        type=str,
        default=None,
        help="Name of the network interface to monitor (e.g., eth0). "
             "If not provided, monitors total usage across all interfaces."
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=None,
        help="Threshold in MB above which usage during an interval triggers a warning."
    )
    parser.add_argument(
        "-o", "--csv-output",
        type=str,
        default=None,
        help="Path to a CSV file where usage data will be logged."
    )
    return parser.parse_args()


def get_bandwidth_usage(interval, interface=None):
    """
    Measure network bandwidth usage over a given interval.

    Parameters
    ----------
    interval : float
        Time interval in seconds between checks.
    interface : str, optional
        Specific network interface to monitor.

    Returns
    -------
    tuple
        Upload speed (KB/s), download speed (KB/s)
    """
    if interface:
        net_io_before = psutil.net_io_counters(pernic=True).get(interface)
    else:
        net_io_before = psutil.net_io_counters()
    
    time.sleep(interval)

    if interface:
        net_io_after = psutil.net_io_counters(pernic=True).get(interface)
    else:
        net_io_after = psutil.net_io_counters()
    
    if not net_io_before or not net_io_after:
        print(f"Error: Interface '{interface}' not found.")
        sys.exit(1)
    
    sent_bytes = net_io_after.bytes_sent - net_io_before.bytes_sent
    received_bytes = net_io_after.bytes_recv - net_io_before.bytes_recv
    
    sent_speed = sent_bytes / interval / 1024  # Convert to KB/s
    received_speed = received_bytes / interval / 1024  # Convert to KB/s

    return sent_speed, received_speed


def log_to_csv(csv_path, upload_speed, download_speed):
    """
    Log bandwidth usage data to a CSV file.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file.
    upload_speed : float
        Upload speed in KB/s.
    download_speed : float
        Download speed in KB/s.
    """
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), upload_speed, download_speed])


def main():
    args = parse_arguments()
    print("Starting network bandwidth monitoring. Press Ctrl+C to stop.")
    
    try:
        while True:
            upload_speed, download_speed = get_bandwidth_usage(args.interval, args.interface)
            print(f"Upload Speed: {upload_speed:.2f} KB/s, Download Speed: {download_speed:.2f} KB/s")
            
            if args.threshold and (upload_speed / 1024 > args.threshold or download_speed / 1024 > args.threshold):
                print("Warning: Bandwidth usage exceeded threshold!")
            
            if args.csv_output:
                log_to_csv(args.csv_output, upload_speed, download_speed)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
