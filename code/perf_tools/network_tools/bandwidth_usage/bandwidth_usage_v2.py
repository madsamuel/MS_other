import psutil
import time
import argparse
import csv
import sys
from datetime import datetime


def parse_arguments():
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Monitor network bandwidth usage over specified intervals."
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Interval between usage checks in seconds (default: 1.0)."
    )
    parser.add_argument(
        "-n", "--interface",
        type=str,
        default=None,
        help="Network interface to monitor (e.g., eth0). Defaults to all interfaces."
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=None,
        help="Threshold in MB triggering a warning if exceeded during interval."
    )
    parser.add_argument(
        "-o", "--csv-output",
        type=str,
        default=None,
        help="CSV file path for logging usage data."
    )
    return parser.parse_args()


def get_bandwidth_usage(interval=1.0, interface=None):
    """
    Calculate network bandwidth usage over a specified interval.

    Parameters
    ----------
    interval : float
        Measurement interval in seconds.
    interface : str
        Specific network interface, if monitoring individually.

    Returns
    -------
    tuple
        (sent_MB, received_MB) - Data sent and received in MB.
    """
    counters = psutil.net_io_counters(pernic=True if interface else False)

    net_io_before = counters.get(interface) if interface else counters
    if not net_io_before:
        raise ValueError(f"Interface '{interface}' not found.")

    time.sleep(interval)

    counters = psutil.net_io_counters(pernic=True if interface else False)
    net_io_after = counters.get(interface) if interface else counters
    if not net_io_after:
        raise ValueError(f"Interface '{interface}' not found after interval.")

    sent_mb = (net_io_after.bytes_sent - net_io_before.bytes_sent) / (1024 * 1024)
    received_mb = (net_io_after.bytes_recv - net_io_before.bytes_recv) / (1024 * 1024)

    return sent_mb, received_mb


def log_to_csv(writer, sent_mb, received_mb, total_sent, total_received):
    """Log bandwidth usage data to a CSV file."""
    writer.writerow([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        f"{sent_mb:.2f}",
        f"{received_mb:.2f}",
        f"{total_sent:.2f}",
        f"{total_received:.2f}"
    ])


def monitor_bandwidth(interval=1.0, interface=None, threshold=None, csv_output=None):
    """
    Continuously monitor network bandwidth.

    Parameters
    ----------
    interval : float
        Time interval for measurements.
    interface : str
        Network interface to monitor.
    threshold : float
        Threshold triggering usage warnings.
    csv_output : str
        Path to CSV file for logging.
    """
    total_sent, total_received = 0.0, 0.0

    csv_file, csv_writer = None, None
    if csv_output:
        csv_file = open(csv_output, "a", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        if csv_file.tell() == 0:
            csv_writer.writerow([
                "Timestamp", "IntervalSentMB", "IntervalReceivedMB",
                "TotalSentMB", "TotalReceivedMB"
            ])

    print(f"\nStarting bandwidth monitoring (interval: {interval}s)."
          f" {f'Interface: {interface}.' if interface else 'All interfaces.'}")
    print("Press Ctrl+C to terminate.\n")

    try:
        while True:
            sent_mb, received_mb = get_bandwidth_usage(interval, interface)
            total_sent += sent_mb
            total_received += received_mb

            print(f"[Interval] Sent: {sent_mb:.2f} MB, Received: {received_mb:.2f} MB | "
                  f"[Total] Sent: {total_sent:.2f} MB, Received: {total_received:.2f} MB")

            if threshold:
                if sent_mb > threshold:
                    print(f"WARNING: Sent data ({sent_mb:.2f} MB) exceeded threshold ({threshold} MB).")
                if received_mb > threshold:
                    print(f"WARNING: Received data ({received_mb:.2f} MB) exceeded threshold ({threshold} MB).")

            if csv_writer:
                log_to_csv(csv_writer, sent_mb, received_mb, total_sent, total_received)
                csv_file.flush()

    except KeyboardInterrupt:
        print("\nMonitoring terminated by user.")
    finally:
        if csv_file:
            csv_file.close()

    print(f"\nFinal Usage: Sent: {total_sent:.2f} MB, Received: {total_received:.2f} MB")


def main():
    """Entry point for CLI execution."""
    args = parse_arguments()

    try:
        monitor_bandwidth(
            interval=args.interval,
            interface=args.interface,
            threshold=args.threshold,
            csv_output=args.csv_output
        )
    except ValueError as error:
        sys.exit(f"Error: {error}")


if __name__ == "__main__":
    main()