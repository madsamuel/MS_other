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


def get_bandwidth_usage(interval=1.0, interface=None):
    """
    Measure network bandwidth usage over a given interval, optionally for a specific interface.

    Parameters
    ----------
    interval : float
        Time interval in seconds over which to measure usage.
    interface : str
        Name of the network interface to monitor. If None, captures total usage.

    Returns
    -------
    tuple
        A tuple of two floats: (sent_usage_in_mb, received_usage_in_mb).
        Represents the amount of data sent and received in MB during the interval.
    """
    if interface:
        # Get the counters for the specified interface only
        net_io_before = psutil.net_io_counters(pernic=True).get(interface)
        if not net_io_before:
            raise ValueError(f"Interface '{interface}' not found. Please check the name.")
    else:
        net_io_before = psutil.net_io_counters()

    if net_io_before is None:
        raise ValueError("Unable to retrieve network counters.")

    time.sleep(interval)

    if interface:
        net_io_after = psutil.net_io_counters(pernic=True).get(interface)
        if not net_io_after:
            raise ValueError(f"Interface '{interface}' not found after sleep. Please check the name.")
    else:
        net_io_after = psutil.net_io_counters()

    sent_bytes = net_io_after.bytes_sent - net_io_before.bytes_sent
    received_bytes = net_io_after.bytes_recv - net_io_before.bytes_recv

    sent_usage_mb = sent_bytes / (1024 * 1024)
    received_usage_mb = received_bytes / (1024 * 1024)

    return sent_usage_mb, received_usage_mb


def monitor_bandwidth(interval=1.0, interface=None, threshold=None, csv_output=None):
    """
    Continuously monitor and display cumulative network bandwidth usage.

    Parameters
    ----------
    interval : float
        Time interval in seconds between usage checks.
    interface : str
        Name of the network interface to monitor. If None, monitors total usage.
    threshold : float
        Usage threshold in MB that triggers a warning if exceeded during an interval.
    csv_output : str
        Optional file path to log usage data in CSV format.
    """
    total_sent_mb = 0.0
    total_received_mb = 0.0

    # Prepare CSV logging if requested
    csv_file = None
    csv_writer = None
    if csv_output:
        csv_file = open(csv_output, mode="a", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        # Write headers if the file is empty
        if csv_file.tell() == 0:
            csv_writer.writerow(["Timestamp", "IntervalSentMB", "IntervalReceivedMB", 
                                 "TotalSentMB", "TotalReceivedMB"])

    print(f"\nMonitoring bandwidth usage every {interval} second(s). "
          f"{f'Interface: {interface}. ' if interface else 'All interfaces. '}"
          "Press Ctrl+C to stop.\n")

    try:
        while True:
            sent_mb, received_mb = get_bandwidth_usage(interval=interval, interface=interface)
            total_sent_mb += sent_mb
            total_received_mb += received_mb

            # Print current usage
            print(
                f"[Interval] Sent: {sent_mb:.2f} MB, Received: {received_mb:.2f} MB | "
                f"[Total] Sent: {total_sent_mb:.2f} MB, Received: {total_received_mb:.2f} MB"
            )

            # Check threshold
            if threshold is not None:
                if sent_mb > threshold:
                    print(f"WARNING: Interval sent ({sent_mb:.2f} MB) exceeded threshold ({threshold} MB).")
                if received_mb > threshold:
                    print(f"WARNING: Interval received ({received_mb:.2f} MB) exceeded threshold ({threshold} MB).")

            # Write to CSV if requested
            if csv_writer:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([timestamp, f"{sent_mb:.2f}", f"{received_mb:.2f}",
                                     f"{total_sent_mb:.2f}", f"{total_received_mb:.2f}"])
                csv_file.flush()

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    finally:
        if csv_file:
            csv_file.close()

    # Final summary
    print(
        f"\nFinal Bandwidth Usage - Sent: {total_sent_mb:.2f} MB, "
        f"Received: {total_received_mb:.2f} MB"
    )


def main():
    """
    Main entry point for running the bandwidth monitor with CLI arguments.
    """
    args = parse_arguments()

    try:
        monitor_bandwidth(
            interval=args.interval,
            interface=args.interface,
            threshold=args.threshold,
            csv_output=args.csv_output
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
